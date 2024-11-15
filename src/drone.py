# src/drone.py

import math
from typing import Tuple

class Drone:
    BASE_SPEED = 30  # Velocidade base do drone em Km/h
    MAX_SPEED = 60   # Velocidade máxima do drone em Km/h
    BASE_AUTONOMY = 1800  # Autonomia total em segundos (30 minutos)

    def __init__(self, initial_position, battery, weather, navigation):
        """
        Inicializa o drone com a posição inicial e instâncias de bateria, clima e navegação.
        """
        self.position = initial_position
        self.speed = self.BASE_SPEED
        self.battery = battery
        self.weather = weather
        self.navigation = navigation
        self.remaining_autonomy = self.BASE_AUTONOMY

    def consume_autonomy(self, duration):
        """
        Consome a autonomia do drone com base na duração do voo em segundos.
        Retorna True se há autonomia suficiente, False caso contrário.
        """
        if self.remaining_autonomy >= duration:
            self.remaining_autonomy -= duration
            self.battery.consume_charge(duration)
            return True
        
        print(f"Autonomia insuficiente! Necessário: {duration}s, Disponível: {self.remaining_autonomy}s")
        return False

    def move_to(self, target_position):
        """
        Move o drone para a posição de destino, ajustando-se às condições do vento e ao consumo de bateria.
        """
        # Calcular a distância
        distance = self.navigation.calculate_distance(self.position, target_position)
        print(f"Distância a percorrer: {distance:.2f} km")
        
        # Obter dados de vento
        current_time = self.navigation.get_current_time().strftime("%Hh")
        wind = self.weather.get_wind_for_time(current_time)
        
        # Ajustar velocidade efetiva considerando o vento
        if wind and 'speed_kmh' in wind:
            # Ventos contrários (E, NE, ENE, SE) reduzem a velocidade diretamente
            if wind['direction'] in ['E', 'NE', 'ENE', 'SE']:
                effective_speed = max(1, self.speed - wind['speed_kmh'])
            # Ventos favoráveis (W, NW, WSW, SW) podem aumentar a velocidade
            elif wind['direction'] in ['W', 'NW', 'WSW', 'SW']:
                effective_speed = min(self.MAX_SPEED, self.speed + (wind['speed_kmh'] * 0.5))
            else:
                effective_speed = self.speed
                
            print(f"Velocidade do vento: {wind['speed_kmh']} km/h, Direção: {wind['direction']}")
        else:
            effective_speed = self.speed
            print("Sem dados de vento disponíveis")
        
        print(f"Velocidade efetiva do drone: {effective_speed} km/h")

        # Calcular tempo de voo
        flight_time = math.ceil((distance / effective_speed) * 3600)
        takeoff_landing_time = 60  # Tempo fixo para decolagem e pouso
        total_time = flight_time + takeoff_landing_time
        
        print(f"Tempo de voo estimado: {flight_time} segundos")
        print(f"Tempo total necessário: {total_time} segundos")
        
        # Verificar autonomia
        if not self.consume_autonomy(total_time):
            return False

        # Atualizar posição
        self.position = target_position
        return True

    def adjust_for_wind(self, wind_data):
        """
        Ajusta a velocidade e direção do drone conforme os dados do vento.
        """
        wind_speed = wind_data["speed"]
        wind_direction = wind_data["direction"]

        if wind_direction in ["N", "NE", "E", "SE", "S"]:
            effective_speed = max(1, self.speed - wind_speed * 0.2)
        elif wind_direction in ["NW", "W", "SW"]:
            effective_speed = min(self.MAX_SPEED, self.speed + wind_speed * 0.1)
        else:
            effective_speed = self.speed

        # Ajusta a velocidade sem ultrapassar a velocidade máxima
        self.speed = round(min(self.MAX_SPEED, effective_speed))
        if self.speed > self.BASE_SPEED:
            self.increase_battery_consumption()

    def increase_battery_consumption(self):
        """
        Aumenta o consumo de autonomia quando o drone opera acima da velocidade base.
        """
        extra_consumption = (self.speed - self.BASE_SPEED) * 0.05  # Exemplo de fator de aumento
        self.remaining_autonomy = max(0, self.remaining_autonomy - extra_consumption)

    def calculate_flight_time(self, distance):
        """
        Calcula o tempo de voo em segundos com base na distância em quilômetros
        e na velocidade atual do drone.
        """
        # Converte a velocidade para km/s e calcula o tempo
        return math.ceil((distance / self.speed) * 3600)  # Retorna apenas o tempo de voo

    def can_reach(self, target_position: Tuple[float, float]) -> bool:
        """
        Verifica se o drone pode alcançar um ponto com a autonomia atual.
        """
        # Calcula distância
        distance = self.navigation.calculate_distance(self.position, target_position)
        
        # Obtém condições do vento
        current_time = self.navigation.get_current_time().strftime("%Hh")
        wind = self.weather.get_wind_for_time(current_time)
        
        # Calcula velocidade efetiva
        if wind and 'speed_kmh' in wind:
            if wind['direction'] in ['E', 'NE', 'ENE', 'SE']:
                effective_speed = max(1, self.speed - wind['speed_kmh'])
            elif wind['direction'] in ['W', 'NW', 'WSW', 'SW']:
                effective_speed = min(self.MAX_SPEED, self.speed + (wind['speed_kmh'] * 0.5))
            else:
                effective_speed = self.speed
        else:
            effective_speed = self.speed
        
        # Calcula tempo necessário
        flight_time = math.ceil((distance / effective_speed) * 3600)
        total_time = flight_time + 60  # Inclui tempo de decolagem/pouso
        
        # Verifica se tem autonomia suficiente
        return self.remaining_autonomy >= total_time

    def __str__(self):
        """
        Representação textual do drone com suas principais informações.
        """
        return f"Drone(position={self.position}, speed={self.speed}, battery={self.battery.current_charge}%, autonomy={self.remaining_autonomy}s)"
