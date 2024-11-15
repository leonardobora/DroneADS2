import csv
from typing import List, Tuple, Dict
from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.cep_mapper import CEPMapper

class RouteManager:
    def __init__(self, csv_path: str, limit: int = None):
        """
        Inicializa o gerenciador de rotas com o caminho para o arquivo CSV de coordenadas.
        :param csv_path: Caminho para o arquivo CSV
        :param limit: Número máximo de coordenadas a carregar (opcional)
        """
        self.coordinates = []  # Lista de tuplas (longitude, latitude)
        self.load_coordinates(csv_path, limit)
        self.cep_mapper = CEPMapper('data/coordenadas.csv')

    def load_coordinates(self, csv_path: str, limit: int = None) -> None:
        """
        Carrega coordenadas do arquivo CSV.
        :param csv_path: Caminho para o arquivo CSV
        :param limit: Número máximo de coordenadas a carregar (opcional)
        """
        self.coordinates = []  # Limpa coordenadas existentes
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                if limit and i >= limit:
                    break
                coord = (float(row['longitude']), float(row['latitude']))
                self.coordinates.append(coord)
    
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
        for coord in self.coordinates:
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
        drone = Drone(
            initial_position=start_coord,
            battery=Battery(100),
            weather=Weather(),
            navigation=Navigation()
        )
        drone.remaining_autonomy = autonomy
        
        route = [start_coord]
        current_pos = start_coord
        
        while len(route) < max_points:
            # Encontra próximo melhor ponto considerando:
            # 1. Distância
            # 2. Condições do vento
            # 3. Autonomia restante
            best_next = None
            best_score = float('inf')
            
            for coord in self.coordinates:
                if coord not in route:
                    # Simula movimento
                    distance = drone.navigation.calculate_distance(current_pos, coord)
                    wind = drone.weather.get_wind_for_time(drone.navigation.get_current_time().strftime("%Hh"))
                    
                    # Calcula score (menor é melhor)
                    wind_penalty = wind['speed_kmh'] if wind and wind['direction'] in ['E', 'NE', 'ENE', 'SE'] else 0
                    score = distance + (wind_penalty * 0.5)
                    
                    if score < best_score:
                        # Verifica se tem autonomia
                        test_drone = Drone(current_pos, Battery(100), Weather(), Navigation())
                        test_drone.remaining_autonomy = drone.remaining_autonomy
                        
                        if test_drone.move_to(coord):
                            best_score = score
                            best_next = coord
            
            if best_next is None:
                break
                
            # Atualiza rota e posição
            route.append(best_next)
            current_pos = best_next
            drone.position = best_next
            
        return route

    def find_charging_points(self, current_position: Tuple[float, float], remaining_autonomy: int) -> List[Tuple[float, float]]:
        """
        Encontra pontos de recarga alcançáveis com a autonomia atual.
        Retorna lista ordenada por proximidade.
        """
        charging_points = [
            (-49.2160678044742, -25.4233146347775),  # Base UniBrasil
            (-49.2733, -25.4284),                     # Centro
            (-49.2336060009616, -25.4300625729625),  # Norte
            (-49.2047594214569, -25.4608672106041),  # Leste
            (-49.3400481020638, -25.4936598469491),  # Oeste
        ]
        
        drone = Drone(current_position, Battery(100), Weather(), Navigation())
        drone.remaining_autonomy = remaining_autonomy
        
        reachable = []
        for point in charging_points:
            if drone.can_reach(point):
                distance = drone.navigation.calculate_distance(current_position, point)
                reachable.append((distance, point))
        
        # Ordena por distância
        reachable.sort(key=lambda x: x[0])
        return [point for _, point in reachable]

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

    def plan_multi_day_route(self, start_coord: Tuple[float, float], days: int = 5) -> List[List[Tuple[float, float]]]:
        """
        Planeja uma rota distribuída em múltiplos dias, considerando:
        - Condições climáticas diferentes por dia
        - Necessidade de recarga
        - Horários específicos para cada dia
        """
        daily_routes = []
        current_position = start_coord
        
        for day in range(days):
            # Planeja rota para o dia atual
            daily_route = self.plan_optimized_route(
                start_coord=current_position,
                autonomy=28800,  # 8 horas por dia
                max_points=10
            )
            
            daily_routes.append(daily_route)
            current_position = daily_route[-1]  # Próximo dia começa do último ponto
            
        return daily_routes

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