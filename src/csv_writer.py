from typing import List, Tuple, Dict
from datetime import datetime
import csv
from src.cep_mapper import CEPMapper
import os

class CSVWriter:
    """
    Classe responsável por gerar o arquivo CSV de saída com o formato:
    data,horario_saida,horario_chegada,cep_origem,cep_destino,coord_origem,coord_destino,velocidade,pouso
    """
    def __init__(self, cep_mapper: CEPMapper):
        if cep_mapper is None:
            raise ValueError("cep_mapper não pode ser None")
        self.cep_mapper = cep_mapper
        self.output_dir = 'output'
        os.makedirs(self.output_dir, exist_ok=True)  # Cria a pasta output se não existir

    def format_coord(self, coord: Tuple[float, float]) -> str:
        """Formata coordenadas como string no formato 'longitude,latitude'"""
        return f"{coord[0]},{coord[1]}"

    def format_time(self, time: datetime) -> str:
        """Formata horário no padrão HH:MM:SS"""
        return time.strftime("%H:%M:%S")

    def write_route(self, filename: str, route_data: List[Dict]) -> None:
        """
        Escreve a rota no arquivo CSV.
        
        route_data: Lista de dicionários com as informações de cada trecho:
        {
            'date': datetime,
            'departure_time': datetime,
            'arrival_time': datetime,
            'origin_coord': (lon, lat),
            'dest_coord': (lon, lat),
            'speed': float,
            'landing': bool
        }
        """
        filepath = os.path.join(self.output_dir, filename)  # Caminho completo do arquivo
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escreve cabeçalho
            writer.writerow([
                'data',
                'horario_saida',
                'horario_chegada',
                'cep_origem',
                'cep_destino',
                'coord_origem',
                'coord_destino',
                'velocidade',
                'pouso'
            ])
            
            # Escreve cada trecho da rota
            for segment in route_data:
                # Obtém CEPs a partir das coordenadas
                origin_cep = self.cep_mapper.get_cep(segment['origin_coord'])
                dest_cep = self.cep_mapper.get_cep(segment['dest_coord'])
                
                writer.writerow([
                    segment['date'].strftime("%Y-%m-%d"),
                    self.format_time(segment['departure_time']),
                    self.format_time(segment['arrival_time']),
                    origin_cep,
                    dest_cep,
                    self.format_coord(segment['origin_coord']),
                    self.format_coord(segment['dest_coord']),
                    f"{segment['speed']:.1f}",
                    '1' if segment['landing'] else '0'
                ]) 