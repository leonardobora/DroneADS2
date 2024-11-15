import pytest
from src.cep_mapper import CEPMapper
import tempfile
import csv
import os

class TestCEPMapper:
    @pytest.fixture
    def sample_csv(self):
        # Criar arquivo CSV temporário para testes
        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['cep', 'longitude', 'latitude'])
            writer.writerow(['80010-010', -49.2722, -25.4288])  # CEP válido
            writer.writerow(['82990-198', -49.3722, -25.5288])  # CEP válido
            writer.writerow(['90000-000', -49.4722, -25.6288])  # CEP inválido
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)  # Limpa o arquivo após os testes

    def test_format_cep(self):
        mapper = CEPMapper("dummy.csv")  # O arquivo não será usado neste teste
        
        # Testa diferentes formatos de entrada
        assert mapper.format_cep("80010010") == "80010-010"
        assert mapper.format_cep("80010-010") == "80010-010"
        assert mapper.format_cep("80.010.010") == "80010-010"
        
        # Testa CEP inválido
        with pytest.raises(ValueError):
            mapper.format_cep("800100")
    
    def test_validate_cep(self):
        mapper = CEPMapper("dummy.csv")
        
        # Testa CEPs válidos
        assert mapper.validate_cep("80010-010") == True
        assert mapper.validate_cep("82990-198") == True
        
        # Testa CEPs inválidos
        assert mapper.validate_cep("90000-000") == False
        assert mapper.validate_cep("70000-000") == False
    
    def test_load_ceps(self, sample_csv):
        mapper = CEPMapper(sample_csv)
        
        # Verifica se apenas os CEPs válidos foram carregados
        assert len(mapper.cep_map) == 2
        assert len(mapper.coord_map) == 2
        
        # Verifica se as coordenadas foram mapeadas corretamente
        assert mapper.get_coordinates("80010-010") == (-49.2722, -25.4288)
        assert mapper.get_coordinates("82990-198") == (-49.3722, -25.5288)
    
    def test_get_cep(self, sample_csv):
        mapper = CEPMapper(sample_csv)
        
        # Testa busca exata
        coord_exato = (-49.2722, -25.4288)
        assert mapper.get_cep(coord_exato) == "80010-010"
        
        # Testa busca por proximidade
        coord_proximo = (-49.2723, -25.4289)  # Coordenada muito próxima
        assert mapper.get_cep(coord_proximo, max_distance=0.1) == "80010-010"
        
        # Testa coordenada muito distante
        coord_distante = (-48.0000, -24.0000)
        assert mapper.get_cep(coord_distante, max_distance=1.0) is None
        
        # Testa entrada inválida
        with pytest.raises(ValueError):
            mapper.get_cep((-49.2722,))  # Tupla incompleta
    
    def test_get_coordinates(self, sample_csv):
        mapper = CEPMapper(sample_csv)
        
        # Testa CEP válido
        coords = mapper.get_coordinates("80010-010")
        assert coords == (-49.2722, -25.4288)
        
        # Testa CEP inexistente
        assert mapper.get_coordinates("80000-000") is None
        
        # Testa CEP em formato diferente
        coords = mapper.get_coordinates("80010010")
        assert coords == (-49.2722, -25.4288)