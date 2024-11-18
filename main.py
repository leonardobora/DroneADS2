import logging
from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.route_manager import RouteManager
from src.route_visualizer import RouteVisualizer
from src.genetic_algorithm import DroneGeneticAlgorithm
from src.csv_writer import CSVWriter
from src.cep_mapper import CEPMapper
from typing import List, Tuple
from datetime import datetime, timedelta

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simulate_day_route(route, base_position, day_number):
    """Simula a rota de um dia e retorna estatísticas"""
    drone = Drone(base_position, Battery(100), Weather(), Navigation())
    initial_autonomy = drone.remaining_autonomy = 1800  # 30 minutos em segundos
    
    total_distance = 0
    total_time = 0
    wind_impact = 0
    recharge_count = 0
    
    for i in range(len(route) - 1):
        current, next_point = route[i], route[i + 1]
        
        # Verifica recarga
        if not drone.can_reach(next_point):
            recharge_count += 1
            drone.remaining_autonomy = initial_autonomy
        
        # Move drone
        autonomy_before = drone.remaining_autonomy
        if drone.move_to(next_point):
            distance = drone.navigation.calculate_distance(current, next_point)
            total_distance += distance
            time_used = autonomy_before - drone.remaining_autonomy
            total_time += time_used
            
            # Impacto do vento
            wind = drone.weather.get_wind_for_time(drone.navigation.get_current_time().strftime("%Hh"))
            if wind and wind['direction'] in ['E', 'NE', 'ENE', 'SE']:
                wind_impact += (wind['speed_kmh'] / drone.BASE_SPEED) * 100
    
    return {
        'total_distance': total_distance,
        'total_time': total_time,
        'energy_consumption': (total_time / initial_autonomy) * 100,
        'wind_impact': wind_impact / len(route) if len(route) > 0 else 0,
        'recharge_count': recharge_count
    }

def get_genetic_algorithm_config() -> dict:
    """Retorna a configuração do algoritmo genético."""
    return {
        'population_size': 200,    # Tamanho da população
        'generations': 1000,        # Número de gerações
        'mutation_rate': 0.2,     # Taxa de mutação
        'elite_size': 60           # Número de melhores indivíduos a preservar
    }

def main():
    logging.info("=== Sistema de Entrega por Drone - Otimização com Todos os CEPs ===")
    
    # Instanciar o CEPMapper
    cep_mapper = CEPMapper('data/coordenadas.csv')  
    
    # Usar todos os pontos disponíveis
    route_manager = RouteManager('data/coordenadas.csv')
    visualizer = RouteVisualizer(route_manager)
    base_position = (-49.2160678044742, -25.4233146347775)
    
    # 
    daily_routes = route_manager.plan_multi_day_route(base_position, days=5, autonomy=1800)
    
    all_routes = []
    analysis_data = {}
    
    # Obter configuração do algoritmo genético
    ga_config = get_genetic_algorithm_config()
    
    for day, points in enumerate(daily_routes, 1):
        logging.info(f"\nDia {day}: Otimizando {len(points)} pontos...")
        
        ga = DroneGeneticAlgorithm(
            coordinates=points,
            base_position=base_position,
            cep_mapper=cep_mapper,  
            population_size=ga_config['population_size'],
            generations=ga_config['generations'],
            mutation_rate=ga_config['mutation_rate'],
            elite_size=ga_config['elite_size']
        )
        
        best_route, best_fitness = ga.optimize(verbose=False)
        all_routes.append(best_route)
        
        stats = simulate_day_route(best_route, base_position, day)
        analysis_data[str(day)] = stats
        
        logging.info(f"✓ Rota otimizada: {len(best_route)} pontos, {stats['total_distance']:.1f}km")
    
    # Salva o mapa final
    visualizer.create_map(all_routes, analysis_data, filename='route_map.html')
    
    # Criar CSVWriter com o cep_mapper
    csv_writer = CSVWriter(cep_mapper)
    # Supondo que você tenha uma função para gerar os dados da rota
    route_data = [cep_mapper.map_to_cep(point) for route in all_routes for point in route]
    csv_writer.write_route('rota_final.csv', route_data)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Erro ao executar o programa: {e}")