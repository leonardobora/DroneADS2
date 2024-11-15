import folium
from typing import List, Tuple
from src.route_manager import RouteManager

class RouteVisualizer:
    def __init__(self, route_manager: RouteManager):
        """
        Inicializa o visualizador de rotas.
        :param route_manager: Instância do gerenciador de rotas
        """
        self.route_manager = route_manager

    def create_map(self, routes: List[List[Tuple[float, float]]], 
                   analysis_data: dict = None, 
                   filename: str = 'route_map.html') -> None:
        """
        Cria um mapa interativo com as rotas e relatório detalhado
        :param routes: Lista de rotas para visualizar
        :param analysis_data: Dados de análise para exibir
        :param filename: Nome do arquivo HTML a ser gerado
        """
        # Centro em Curitiba
        m = folium.Map(location=[-25.4284, -49.2733], zoom_start=12)
        
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        # Adiciona relatório em um painel lateral
        html = """
        <div style="position: fixed; 
                    top: 10px; 
                    right: 10px; 
                    width: 300px;
                    height: auto;
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);
                    z-index: 1000;">
            <h3>Relatório de Rotas</h3>
        """
        
        for day, route in enumerate(routes, 1):
            html += f"<h4>Dia {day}</h4>"
            html += f"<p>Pontos visitados: {len(route)}</p>"
            
            if analysis_data and str(day) in analysis_data:
                data = analysis_data[str(day)]
                html += f"""
                <ul>
                    <li>Distância: {data['total_distance']:.2f} km</li>
                    <li>Tempo total: {data['total_time']/3600:.1f} horas</li>
                    <li>Consumo: {data['energy_consumption']:.1f}%</li>
                    <li>Impacto do vento: {data['wind_impact']:.1f}%</li>
                </ul>
                """
            
            # Desenha rota
            points = [(lat, lon) for lon, lat in route]
            folium.PolyLine(
                points,
                weight=2,
                color=colors[day % len(colors)],
                popup=f'Dia {day}'
            ).add_to(m)
            
            # Adiciona marcadores
            for i, point in enumerate(route):
                folium.Marker(
                    [point[1], point[0]],
                    popup=f'Dia {day} - Ponto {i + 1}'
                ).add_to(m)
        
        html += "</div>"
        
        # Adiciona o painel ao mapa
        m.get_root().html.add_child(folium.Element(html))
        
        # Salva com nome personalizado
        m.save(filename) 