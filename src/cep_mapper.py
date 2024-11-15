from typing import Tuple, Dict, Optional
from src.navigation import Navigation
import re

class CEPMapper:
    def __init__(self, csv_path: str):
        self.cep_map: Dict[Tuple[float, float], str] = {}
        self.coord_map: Dict[str, Tuple[float, float]] = {}
        self.navigation = Navigation()
        self.load_ceps(csv_path)
    
    def format_cep(self, cep: str) -> str:
        """
        Formata o CEP para o padrão XXXXX-XXX
        :param cep: CEP em qualquer formato
        :return: CEP formatado
        """
        # Remove todos os caracteres não numéricos
        cep_clean = re.sub(r'\D', '', cep)
        if len(cep_clean) != 8:
            raise ValueError(f"CEP inválido: {cep}. Deve conter 8 dígitos.")
        return f"{cep_clean[:5]}-{cep_clean[5:]}"

    def load_ceps(self, csv_path: str) -> None:
        """
        Carrega CEPs e coordenadas do CSV.
        Formato esperado: cep,longitude,latitude
        """
        import csv
        try:
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        coord = (float(row['longitude']), float(row['latitude']))
                        cep = self.format_cep(row['cep'])
                        if self.validate_cep(cep):
                            self.cep_map[coord] = cep
                            self.coord_map[cep] = coord
                        else:
                            print(f"CEP fora da faixa válida: {cep}")
                    except (ValueError, KeyError) as e:
                        print(f"Erro ao processar linha do CSV: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_path}")
    
    def get_cep(self, coord: Tuple[float, float], max_distance: float = 1.0) -> Optional[str]:
        """
        Retorna CEP exato ou mais próximo das coordenadas dentro de uma distância máxima.
        :param coord: Tupla (longitude, latitude)
        :param max_distance: Distância máxima em km para considerar um CEP válido
        :return: CEP correspondente ou None se nenhum CEP estiver dentro da distância máxima
        """
        if not isinstance(coord, tuple) or len(coord) != 2:
            raise ValueError("Coordenadas devem ser uma tupla (longitude, latitude)")
            
        if coord in self.cep_map:
            return self.cep_map[coord]
        
        min_distance = float('inf')
        nearest_coord = None
        
        for map_coord in self.cep_map.keys():
            distance = self.navigation.calculate_distance(coord, map_coord)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest_coord = map_coord
        
        return self.cep_map[nearest_coord] if nearest_coord else None
    
    def get_coordinates(self, cep: str) -> Optional[Tuple[float, float]]:
        """
        Retorna coordenadas para um CEP.
        :param cep: CEP a buscar (formato XXXXX-XXX ou XXXXXXXX)
        :return: Tupla (longitude, latitude) ou None se não encontrado
        """
        try:
            formatted_cep = self.format_cep(cep)
            return self.coord_map.get(formatted_cep)
        except ValueError:
            return None
    
    def validate_cep(self, cep: str) -> bool:
        """
        Verifica se CEP está na faixa válida (80010-010 a 82990-198).
        Aceita CEP com ou sem hífen.
        """
        try:
            cep_clean = re.sub(r'\D', '', cep)
            cep_num = int(cep_clean)
            return 80010010 <= cep_num <= 82990198
        except ValueError:
            return False