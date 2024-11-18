import math
from typing import Optional, Tuple
from src.cep_mapper import CEPMapper

class Drone:
    BASE_SPEED = 30  # Velocidade base do drone em Km/h
    MAX_SPEED = 60   # Velocidade máxima do drone em Km/h
    BASE_AUTONOMY = 1800  # Autonomia total em segundos (30 minutos)
    MAX_DISTANCE = 50  # Distância máxima que o drone pode percorrer sem recarga em km

    def __init__(self, initial_position: Tuple[float, float], battery, weather, navigation, cep_mapper: CEPMapper):
        """
        Inicializa o drone com a posição inicial e instâncias de bateria, clima, navegação e mapeador de CEP.
        
        Args:
            initial_position (Tuple[float, float]): Posição inicial do drone (latitude, longitude)
            battery: Instância do gerenciador de bateria
            weather: Instância do serviço de clima
            navigation: Instância do serviço de navegação
            cep_mapper (CEPMapper): Instância do mapeador de CEP
        """
        self.position = initial_position
        self.speed = self.BASE_SPEED
        self.battery = battery
        self.weather = weather
        self.navigation = navigation
        self.cep_mapper = cep_mapper
        self.remaining_autonomy = self.BASE_AUTONOMY

    def consume_autonomy(self, duration: int, mode: str = "normal") -> bool:
        """
        Consome a autonomia do drone com base na duração do voo em segundos e no modo de voo.
        
        Args:
            duration (int): Duração do voo em segundos
            mode (str): Modo de voo ("normal" ou "esportivo")
        
        Returns:
            bool: True se há autonomia suficiente, False caso contrário
        """
        if self.remaining_autonomy >= duration:
            self.remaining_autonomy -= duration
            self.battery.consume_charge(duration, mode)
            return True
        
        print(f"Autonomia insuficiente! Necessário: {duration}s, Disponível: {self.remaining_autonomy}s")
        return False

    def move_to(self, target_position: Tuple[float, float]) -> bool:
        """
        Move o drone para a posição de destino, ajustando-se às condições do vento e ao consumo de bateria.
        Inclui pontos de recarga se necessário.
        
        Args:
            target_position (Tuple[float, float]): Posição de destino (latitude, longitude)
            
        Returns:
            bool: True se o movimento foi bem-sucedido, False caso contrário
        """
        # Calcular a distância
        distance = self.navigation.calculate_distance(self.position, target_position)
        print(f"Distância a percorrer: {distance:.2f} km")
        
        # Verificar se a distância excede o máximo permitido
        if distance > self.MAX_DISTANCE:
            print("Distância excessiva. Incluindo pontos de recarga.")
            # Encontrar o ponto de recarga mais próximo
            nearest_charging_point = self.find_nearest_charging_point(self.position)
            if nearest_charging_point:
                # Mover para o ponto de recarga
                if not self.move_to(nearest_charging_point):
                    return False
                # Recarregar bateria e restaurar autonomia
                self.battery.recharge()
                self.remaining_autonomy = self.BASE_AUTONOMY
                # Atualizar a posição após a recarga
                self.position = nearest_charging_point
                # Reduzir a distância para o destino após a recarga
                distance = self.navigation.calculate_distance(self.position, target_position)
                print(f"Distância após recarga: {distance:.2f} km")
            else:
                print("Não foi possível encontrar um ponto de recarga próximo")
                return False
        
        # Obter dados de vento
        current_time = self.navigation.get_current_time().strftime("%Hh")
        wind = self.weather.get_wind_for_time(current_time)
        
        # Ajustar velocidade efetiva considerando o vento
        if wind and 'speed_kmh' in wind:
            # Ventos contrários (E, NE, ENE, SE) reduzem a velocidade diretamente
            if wind['direction'] in ['E', 'NE', 'ENE', 'SE']:
                effective_speed = max(1, self.BASE_SPEED - wind['speed_kmh'])
            # Ventos favoráveis (W, NW, WSW, SW) podem aumentar a velocidade
            elif wind['direction'] in ['W', 'NW', 'WSW', 'SW']:
                effective_speed = min(self.MAX_SPEED, self.BASE_SPEED + (wind['speed_kmh'] * 0.5))
            else:
                effective_speed = self.BASE_SPEED
                
            print(f"Velocidade do vento: {wind['speed_kmh']} km/h, Direção: {wind['direction']}")
        else:
            effective_speed = self.BASE_SPEED
            print("Sem dados de vento disponíveis")
        
        print(f"Velocidade efetiva do drone: {effective_speed} km/h")

        # Determinar o modo de voo
        mode = "normal"
        if effective_speed > self.BASE_SPEED:
            mode = "esportivo"
            self.speed = self.MAX_SPEED
        else:
            self.speed = self.BASE_SPEED

        # Calcular tempo de voo
        flight_time = math.ceil((distance / effective_speed) * 3600)
        takeoff_landing_time = 60  # Tempo fixo para decolagem e pouso
        total_time = flight_time + takeoff_landing_time
        
        print(f"Tempo de voo estimado: {flight_time} segundos")
        print(f"Tempo total necessário: {total_time} segundos")
        
        # Verificar autonomia
        if not self.consume_autonomy(total_time, mode):
            return False

        # Atualizar posição
        self.position = target_position
        return True

    def adjust_for_wind(self, wind_data: dict) -> None:
        """
        Ajusta a velocidade e direção do drone conforme os dados do vento.
        
        Args:
            wind_data (dict): Dicionário contendo velocidade e direção do vento
        """
        wind_speed = wind_data["speed"]
        wind_direction = wind_data["direction"]

        if wind_direction in ["N", "NE", "E", "SE", "S"]:
            effective_speed = max(1, self.BASE_SPEED - wind_speed * 0.2)
        elif wind_direction in ["NW", "W", "SW"]:
            effective_speed = min(self.MAX_SPEED, self.BASE_SPEED + wind_speed * 0.1)
        else:
            effective_speed = self.BASE_SPEED

        # Ajusta a velocidade sem ultrapassar a velocidade máxima
        self.speed = round(min(self.MAX_SPEED, effective_speed))
        if self.speed > self.BASE_SPEED:
            self.increase_battery_consumption()

    def increase_battery_consumption(self) -> None:
        """
        Aumenta o consumo de autonomia quando o drone opera acima da velocidade base.
        """
        extra_consumption = (self.speed - self.BASE_SPEED) * 0.05  
        self.remaining_autonomy = max(0, self.remaining_autonomy - extra_consumption)

    def calculate_flight_time(self, distance: float) -> int:
        """
        Calcula o tempo de voo em segundos com base na distância em quilômetros
        e na velocidade atual do drone.
        
        Args:
            distance (float): Distância em quilômetros
            
        Returns:
            int: Tempo de voo estimado em segundos
        """
        return math.ceil((distance / self.speed) * 3600)

    def can_reach(self, target_position: Tuple[float, float]) -> bool:
        """
        Verifica se o drone pode alcançar um ponto com a autonomia atual.
        
        Args:
            target_position (Tuple[float, float]): Posição de destino (latitude, longitude)
            
        Returns:
            bool: True se o drone pode alcançar o destino, False caso contrário
        """
        # Calcula distância
        distance = self.navigation.calculate_distance(self.position, target_position)
        
        # Obtém condições do vento
        current_time = self.navigation.get_current_time().strftime("%Hh")
        wind = self.weather.get_wind_for_time(current_time)
        
        # Calcula velocidade efetiva
        if wind and 'speed_kmh' in wind:
            if wind['direction'] in ['E', 'NE', 'ENE', 'SE']:
                effective_speed = max(1, self.BASE_SPEED - wind['speed_kmh'])
            elif wind['direction'] in ['W', 'NW', 'WSW', 'SW']:
                effective_speed = min(self.MAX_SPEED, self.BASE_SPEED + (wind['speed_kmh'] * 0.5))
            else:
                effective_speed = self.BASE_SPEED
        else:
            effective_speed = self.BASE_SPEED
        
        # Determinar o modo de voo
        mode = "normal"
        if effective_speed > self.BASE_SPEED:
            mode = "esportivo"

        # Calcula tempo necessário
        flight_time = math.ceil((distance / effective_speed) * 3600)
        total_time = flight_time + 60  # Inclui tempo de decolagem/pouso
        
        # Verifica se tem autonomia suficiente
        return self.remaining_autonomy >= total_time

    def find_nearest_charging_point(self, current_position: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """
        Encontra o ponto de recarga mais próximo usando o mapeador de CEP.
        
        Args:
            current_position (Tuple[float, float]): Posição atual do drone (latitude, longitude)
            
        Returns:
            Optional[Tuple[float, float]]: Coordenadas do ponto de recarga mais próximo (latitude, longitude)
                                         ou None se não encontrado
        """
        if not self.cep_mapper:
            print("Erro: Mapeador de CEP não está disponível.")
            return None

        nearest_point = None
        min_distance = float('inf')
        
        for cep, coord in self.cep_mapper.coord_map.items():
            distance = self.navigation.calculate_distance(current_position, coord)
            if distance < min_distance:
                min_distance = distance
                nearest_point = coord
                
        return nearest_point

    def __str__(self) -> str:
        """
        Representação textual do drone com suas principais informações.
        
        Returns:
            str: String formatada com as informações do drone
        """
        return (f"Drone(position={self.position}, "
                f"speed={self.speed}, "
                f"battery={self.battery.current_charge}%, "
                f"autonomy={self.remaining_autonomy}s)")