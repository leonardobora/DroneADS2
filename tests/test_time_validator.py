import pytest
from datetime import datetime, timedelta
from src.time_validator import TimeValidator

class TestTimeValidator:
    def test_is_within_operation_hours(self):
        # Horários válidos
        assert TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 6, 0))
        assert TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 12, 0))
        assert TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 18, 59))
        
        # Horários inválidos
        assert not TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 5, 59))
        assert not TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 19, 1))
        assert not TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 0, 0))
        assert not TimeValidator.is_within_operation_hours(datetime(2024, 3, 15, 23, 59))
    
    def test_validate_operation_window(self):
        # Janela válida
        start = datetime(2024, 3, 15, 8, 0)
        end = datetime(2024, 3, 15, 9, 0)
        assert TimeValidator.validate_operation_window(start, end)
        
        # Início antes do horário permitido
        start = datetime(2024, 3, 15, 5, 0)
        end = datetime(2024, 3, 15, 7, 0)
        assert not TimeValidator.validate_operation_window(start, end)
        
        # Fim após horário permitido
        start = datetime(2024, 3, 15, 18, 0)
        end = datetime(2024, 3, 15, 19, 30)
        assert not TimeValidator.validate_operation_window(start, end)
        
        # Fim antes do início
        start = datetime(2024, 3, 15, 9, 0)
        end = datetime(2024, 3, 15, 8, 0)
        assert not TimeValidator.validate_operation_window(start, end)
    
    def test_calculate_total_stop_time(self):
        # Apenas fotografia
        assert TimeValidator.calculate_total_stop_time(True, False) == timedelta(seconds=60)
        
        # Apenas pouso/decolagem
        assert TimeValidator.calculate_total_stop_time(False, True) == timedelta(seconds=120)
        
        # Ambos
        assert TimeValidator.calculate_total_stop_time(True, True) == timedelta(seconds=180)
        
        # Nenhum
        assert TimeValidator.calculate_total_stop_time(False, False) == timedelta(seconds=0)
    
    def test_get_next_valid_start_time(self):
        # Horário atual dentro do período válido
        current = datetime(2024, 3, 15, 10, 0)
        assert TimeValidator.get_next_valid_start_time(current) == current
        
        # Horário atual antes do início
        current = datetime(2024, 3, 15, 5, 0)
        expected = datetime(2024, 3, 15, 6, 0)
        assert TimeValidator.get_next_valid_start_time(current) == expected
        
        # Horário atual após o fim
        current = datetime(2024, 3, 15, 20, 0)
        expected = datetime(2024, 3, 16, 6, 0)
        assert TimeValidator.get_next_valid_start_time(current) == expected
    
    def test_calculate_arrival_time(self):
        start_time = datetime(2024, 3, 15, 8, 0)
        flight_duration = timedelta(minutes=30)
        
        # Operação válida com foto e pouso
        result = TimeValidator.calculate_arrival_time(
            start_time, flight_duration, True, True)
        assert result is not None
        arrival, next_available = result
        assert arrival == start_time + flight_duration
        assert next_available == arrival + timedelta(seconds=180)
        
        # Operação que ultrapassa horário permitido
        start_time = datetime(2024, 3, 15, 18, 45)
        result = TimeValidator.calculate_arrival_time(
            start_time, flight_duration, True, True)
        assert result is None
        
        # Operação fora do horário permitido
        start_time = datetime(2024, 3, 15, 5, 0)
        result = TimeValidator.calculate_arrival_time(
            start_time, flight_duration, True, True)
        assert result is None 