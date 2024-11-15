from datetime import datetime, time, timedelta
from typing import Optional, Tuple

class TimeValidator:
    """
    Classe responsável por validar e gerenciar restrições de horário do drone:
    - Operação apenas entre 6h e 19h
    - 60s para pouso/decolagem
    - 60s para fotografia
    """
    
    # Constantes de tempo
    OPERATION_START = time(6, 0)  # 6:00
    OPERATION_END = time(19, 0)   # 19:00
    LANDING_TIME = timedelta(seconds=60)
    PHOTO_TIME = timedelta(seconds=60)
    
    @classmethod
    def is_within_operation_hours(cls, dt: datetime) -> bool:
        """Verifica se o horário está dentro do período de operação (6h-19h)"""
        return cls.OPERATION_START <= dt.time() <= cls.OPERATION_END
    
    @classmethod
    def validate_operation_window(cls, start: datetime, end: datetime) -> bool:
        """Verifica se todo o período de operação está dentro do horário permitido"""
        return (cls.is_within_operation_hours(start) and 
                cls.is_within_operation_hours(end) and 
                start < end)
    
    @classmethod
    def calculate_total_stop_time(cls, requires_photo: bool = True, 
                                requires_landing: bool = False) -> timedelta:
        """Calcula tempo total de parada baseado nas operações necessárias"""
        total_time = timedelta()
        
        # Tempo de pouso + decolagem se necessário
        if requires_landing:
            total_time += cls.LANDING_TIME * 2  # pouso + decolagem
            
        # Tempo de fotografia se necessário
        if requires_photo:
            total_time += cls.PHOTO_TIME
            
        return total_time
    
    @classmethod
    def get_next_valid_start_time(cls, current: datetime) -> datetime:
        """
        Retorna o próximo horário válido para início de operação.
        Se o horário atual for após 19h, retorna 6h do dia seguinte.
        """
        if current.time() > cls.OPERATION_END:
            next_day = current + timedelta(days=1)
            return datetime.combine(next_day.date(), cls.OPERATION_START)
        
        if current.time() < cls.OPERATION_START:
            return datetime.combine(current.date(), cls.OPERATION_START)
            
        return current
    
    @classmethod
    def calculate_arrival_time(cls, start_time: datetime, flight_duration: timedelta,
                             requires_photo: bool = True, 
                             requires_landing: bool = False) -> Optional[Tuple[datetime, datetime]]:
        """
        Calcula horário de chegada considerando tempo de voo e operações.
        Retorna tupla (horário_chegada, próximo_horário_disponível) ou None se inválido.
        """
        if not cls.is_within_operation_hours(start_time):
            return None
            
        # Calcula tempo total incluindo paradas
        stop_time = cls.calculate_total_stop_time(requires_photo, requires_landing)
        total_duration = flight_duration + stop_time
        
        arrival_time = start_time + flight_duration
        operation_end_time = arrival_time + stop_time
        
        # Verifica se toda a operação cabe no horário permitido
        if not cls.validate_operation_window(start_time, operation_end_time):
            return None
            
        next_available = operation_end_time
        
        return arrival_time, next_available 