import csv
from typing import List, Tuple, Dict
from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.cep_mapper import CEPMapper
import logging

class RouteManager:
    def __init__(self, csv_file: str, limit: int = None):
        self.csv_file = csv_file
        self.limit = limit
        self.points = self.load_points()

    def load_points(self):
        points = []
        with open(self.csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Ignora o cabeçalho
            for row in reader:
                try:
                    lat = float(row[1])
                    lon = float(row[0])
                    points.append((lon, lat))  # Adiciona como (longitude, latitude)
                    if self.limit and len(points) >= self.limit:
                        break  # Para se o limite for atingido
                except ValueError:
                    continue  # Ignora linhas que não podem ser convertidas
        logging.info(f"Coordenadas carregadas: {points}")  
        return points

    def load_all_points(self):
        # Retorna todos os pontos carregados
        return self.points

    def calculate_travel_time(self, start_point, end_point):
        # Implementação para calcular o tempo de viagem entre dois pontos
        distance = self.calculate_distance(start_point, end_point)
        speed = 13  # Velocidade efetiva do drone em km/h
        time_seconds = (distance / speed) * 3600  # Converte para segundos
        return round(time_seconds)  # Arredonda para cima

    def calculate_distance(self, point1, point2):
        from geopy.distance import great_circle
        # Certifique-se de que os pontos estão na ordem correta (lat, lon)
        return great_circle((point1[1], point1[0]), (point2[1], point2[0])).kilometers

    def select_next_point(self, current_route, remaining_points, drone):
        if not remaining_points:
            return None
        
        best_next = None
        best_score = float('inf')
        
        for point in remaining_points:
            distance = self.calculate_distance(current_route[-1], point)
            if distance < best_score and drone.can_reach(point):
                best_next = point
                best_score = distance
                
        return best_next

    def plan_multi_day_route(self, base_position: Tuple[float, float], days: int, autonomy: int) -> List[List[Tuple[float, float]]]:
        cep_mapper = CEPMapper('data/coordenadas.csv')
        all_points = self.load_all_points()  # Carregar todos os pontos disponíveis
        daily_routes = []
        MAX_TIME_PER_DAY = 28800  # 8 horas em segundos
        
        for day in range(days):
            current_route = []
            current_time = 0
            remaining_points = all_points.copy()  # Copia todos os pontos disponíveis
            
            # Adiciona a base como o primeiro ponto do dia
            current_route.append(base_position)
            
            drone = Drone(base_position, Battery(100), Weather(), Navigation(), cep_mapper)
            drone.remaining_autonomy = autonomy
            
            while remaining_points and current_time < MAX_TIME_PER_DAY:
                next_point = self.select_next_point(current_route, remaining_points, drone)
                if next_point is None:
                    break
                
                travel_time = self.calculate_travel_time(current_route[-1], next_point)
                
                if current_time + travel_time <= MAX_TIME_PER_DAY:
                    current_route.append(next_point)
                    current_time += travel_time
                    remaining_points.remove(next_point)
                    drone.move_to(next_point)
                else:
                    break  # Não há mais tempo para visitar outros pontos
            
            logging.info(f"Pontos planejados para o dia {day}: {current_route}")
            daily_routes.append(current_route)
        
        return daily_routes

    def plan_route(self, start_coord: Tuple[float, float], autonomy: int) -> List[Tuple[float, float]]:
        """
        Planeja uma rota a partir de um ponto inicial, considerando a autonomia disponível.
        Implementação inicial: retorna as 3 coordenadas mais próximas do ponto inicial.
        
        :param start_coord: Coordenada inicial (longitude, latitude)
        :param autonomy: Autonomia em segundos
        :return: Lista de coordenadas formando a rota
        """
        nav = Navigation()
        
        # Calcula distâncias para todos os pontos
        distances = []
        for coord in self.points:
            if coord != start_coord:  # Não incluir o próprio ponto inicial
                dist = nav.calculate_distance(start_coord, coord)
                distances.append((dist, coord))
        
        # Ordena por distância
        distances.sort(key=lambda x: x[0])
        
        # Retorna os 3 pontos mais próximos
        route = [start_coord]
        for _, coord in distances[:3]:
            route.append(coord)
            
        return route 

    def plan_optimized_route(self, start_coord: Tuple[float, float], autonomy: int, max_points: int = 5) -> List[Tuple[float, float]]:
        """
        Planeja uma rota otimizada considerando vento e autonomia.
        
        :param start_coord: Coordenada inicial
        :param autonomy: Autonomia em segundos
        :param max_points: Número máximo de pontos na rota
        :return: Lista de coordenadas formando a rota otimizada
        """
        cep_mapper = CEPMapper('data/coordenadas.csv')
        drone = Drone(
            initial_position=start_coord,
            battery=Battery(100),
            weather=Weather(),
            navigation=Navigation(),
            cep_mapper=cep_mapper
        )
        drone.remaining_autonomy = autonomy
        
        route = [start_coord]
        current_pos = start_coord
        
        available_points = [coord for coord in self.points if coord != start_coord]
        
        if len(available_points) < 1:
            raise ValueError("Não há pontos suficientes disponíveis para otimização.")
        
        while len(route) < max_points and available_points:
            # Encontra próximo melhor ponto considerando:
            # 1. Distância
            # 2. Condições do vento
            # 3. Autonomia restante
            best_next = None
            best_score = float('inf')
            
            for coord in available_points:
                # Simula movimento
                distance = drone.navigation.calculate_distance(current_pos, coord)
                wind = drone.weather.get_wind_for_time(drone.navigation.get_current_time().strftime("%Hh"))
                
                # Calcula score (menor é melhor)
                wind_penalty = wind['speed_kmh'] if wind and wind['direction'] in ['E', 'NE', 'ENE', 'SE'] else 0
                score = distance + (wind_penalty * 0.5)
                
                if score < best_score and drone.can_reach(coord):
                    best_score = score
                    best_next = coord
            
            if best_next is None:
                break
                
            # Atualiza rota e posição
            route.append(best_next)
            current_pos = best_next
            drone.position = best_next
            available_points.remove(best_next)
        
        if len(route) <= 1:
            raise ValueError("Não foi possível otimizar a rota com os pontos disponíveis.")
        
        return route

    def calculate_recharge_cost(self, route: List[Tuple[float, float]]) -> float:
        """
        Calcula custo total de recargas na rota.
        Cada recarga custa R$ 60,00.
        """
        drone = Drone(route[0], Battery(100), Weather(), Navigation())
        recharge_count = 0
        
        for i in range(len(route) - 1):
            current = route[i]
            next_point = route[i + 1]
            
            if not drone.can_reach(next_point):
                recharge_count += 1
                drone.remaining_autonomy = 28800  # Recarrega
                
            drone.move_to(next_point)
        
        return recharge_count * 60.0  # R$ 60,00 por recarga

    def analyze_route_efficiency(self, route: List[Tuple[float, float]]) -> dict:
        """
        Analisa a eficiência da rota considerando:
        - Distância total
        - Consumo de energia
        - Impacto do vento
        - Tempo total
        """
        analysis = {
            'total_distance': 0,
            'total_time': 0,
            'energy_consumption': 0,
            'wind_impact': 0
        }
        
        if not route or len(route) < 2:
            return analysis
        
        drone = Drone(route[0], Battery(100), Weather(), Navigation())
        initial_autonomy = drone.remaining_autonomy = 28800  # 8 horas
        
        for i in range(len(route) - 1):
            current = route[i]
            next_point = route[i + 1]
            
            # Calcula distância
            distance = drone.navigation.calculate_distance(current, next_point)
            analysis['total_distance'] += distance
            
            # Simula movimento e coleta métricas
            autonomy_before = drone.remaining_autonomy
            success = drone.move_to(next_point)
            
            if success:
                # Atualiza métricas
                autonomy_used = autonomy_before - drone.remaining_autonomy
                analysis['total_time'] += autonomy_used
                analysis['energy_consumption'] += (autonomy_used / initial_autonomy) * 100
                
                # Calcula impacto do vento
                wind = drone.weather.get_wind_for_time(drone.navigation.get_current_time().strftime("%Hh"))
                if wind and wind['direction'] in ['E', 'NE', 'ENE', 'SE']:
                    analysis['wind_impact'] += (wind['speed_kmh'] / drone.BASE_SPEED) * 100
            else:
                # Se não conseguiu completar o movimento, ajusta métricas
                analysis['total_time'] += autonomy_before
                analysis['energy_consumption'] += 100
                break
        
        return analysis

    def export_route_csv(self, route: List[Dict], filename: str):
        """
        Exporta rota no formato especificado:
        CEP inicial, Lat inicial, Long inicial, Dia, Hora inicial, Velocidade,
        CEP final, Lat final, Long final, Pouso, Hora final
        """
        import csv
        from datetime import datetime, timedelta
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'CEP inicial', 'Latitude inicial', 'Longitude inicial',
                'Dia', 'Hora inicial', 'Velocidade',
                'CEP final', 'Latitude final', 'Longitude final',
                'Pouso', 'Hora final'
            ])
            
            for segment in route:
                writer.writerow([
                    segment['cep_inicial'],
                    segment['lat_inicial'],
                    segment['long_inicial'],
                    segment['dia'],
                    segment['hora_inicial'].strftime('%H:%M:%S'),
                    segment['velocidade'],
                    segment['cep_final'],
                    segment['lat_final'],
                    segment['long_final'],
                    'SIM' if segment['pouso'] else 'NÃO',
                    segment['hora_final'].strftime('%H:%M:%S')
                ])

    def find_charging_points(self, current_position: Tuple[float, float], remaining_autonomy: int) -> List[Tuple[float, float]]:
        reachable_points = []
        for point in self.coordinates:
            distance = self.calculate_distance(current_position, point)
            if distance <= remaining_autonomy / 360:  # Considera autonomia em km
                reachable_points.append(point)
        return reachable_points