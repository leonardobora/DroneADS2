import pytest
from datetime import datetime
from src.csv_writer import CSVWriter
from src.cep_mapper import CEPMapper
import os
import csv

class TestCSVWriter:
    @pytest.fixture
    def sample_cep_mapper(self):
        # Cria um CEPMapper com alguns dados de teste
        mapper = CEPMapper("dummy.csv")  # O arquivo não será usado pois vamos mockar os métodos
        
        # Mock do método get_cep
        def mock_get_cep(coord):
            coords_to_cep = {
                (-49.2722, -25.4288): "80010-010",
                (-49.3722, -25.5288): "82990-198"
            }
            return coords_to_cep.get(coord)
            
        mapper.get_cep = mock_get_cep
        return mapper

    @pytest.fixture
    def sample_route_data(self):
        return [
            {
                'date': datetime(2024, 3, 15),
                'departure_time': datetime(2024, 3, 15, 8, 0, 0),
                'arrival_time': datetime(2024, 3, 15, 8, 15, 0),
                'origin_coord': (-49.2722, -25.4288),
                'dest_coord': (-49.3722, -25.5288),
                'speed': 30.5,
                'landing': True
            }
        ]

    def test_format_coord(self, sample_cep_mapper):
        writer = CSVWriter(sample_cep_mapper)
        coord = (-49.2722, -25.4288)
        assert writer.format_coord(coord) == "-49.2722,-25.4288"

    def test_format_time(self, sample_cep_mapper):
        writer = CSVWriter(sample_cep_mapper)
        time = datetime(2024, 3, 15, 8, 0, 0)
        assert writer.format_time(time) == "08:00:00"

    def test_write_route(self, sample_cep_mapper, sample_route_data, tmp_path):
        # Cria arquivo temporário para teste
        test_file = tmp_path / "test_route.csv"
        
        writer = CSVWriter(sample_cep_mapper)
        writer.write_route(str(test_file), sample_route_data)
        
        # Verifica se arquivo foi criado
        assert test_file.exists()
        
        # Lê arquivo e verifica conteúdo
        with open(test_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            
            row = rows[0]
            assert row['data'] == "2024-03-15"
            assert row['horario_saida'] == "08:00:00"
            assert row['horario_chegada'] == "08:15:00"
            assert row['cep_origem'] == "80010-010"
            assert row['cep_destino'] == "82990-198"
            assert row['coord_origem'] == "-49.2722,-25.4288"
            assert row['coord_destino'] == "-49.3722,-25.5288"
            assert row['velocidade'] == "30.5"
            assert row['pouso'] == "1" 