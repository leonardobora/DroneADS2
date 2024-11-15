import math
from datetime import datetime, timedelta

class Navigation:
    EARTH_RADIUS = 6371  # Raio médio da Terra em quilômetros

    def calculate_distance(self, coord1, coord2):
        """
        Calcula a distância entre duas coordenadas (longitude, latitude) usando a fórmula de Haversine.
        Retorna a distância em quilômetros.
        """
        lon1, lat1 = coord1
        lon2, lat2 = coord2

        # Converte graus para radianos
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Diferenças nas coordenadas
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Calcula a distância
        distance = self.EARTH_RADIUS * c
        
        return distance

    def get_current_time(self):
        """
        Retorna a hora atual, que pode ser usada para simular condições de vento.
        """
        return datetime.now()

    def validate_time(self, time: datetime) -> bool:
        """Verifica se horário está entre 6h e 19h"""
        return 6 <= time.hour < 19

    def calculate_arrival_time(self, start_time: datetime, 
                             distance: float, 
                             speed: float) -> datetime:
        """Calcula hora de chegada considerando distância e velocidade"""
        flight_time = (distance / speed) * 3600  # segundos
        return start_time + timedelta(seconds=int(flight_time))

    def __str__(self):
        """
        Representação textual da navegação.
        """
        return "Navigation system ready"
