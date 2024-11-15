from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.route_manager import RouteManager
from src.route_visualizer import RouteVisualizer
from src.genetic_algorithm import DroneGeneticAlgorithm

def simulate_day_route(route, base_position, day_number):
    """Simula a rota de um dia e retorna estatísticas"""
    drone = Drone(base_position, Battery(100), Weather(), Navigation())
    initial_autonomy = drone.remaining_autonomy = 28800  # 8 horas
    
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

def main():
    print("=== Sistema de Entrega por Drone - Otimização 5 dias ===")
    
    # Reduz para 100 pontos (20 por dia)
    route_manager = RouteManager('data/coordenadas.csv', limit=100)
    visualizer = RouteVisualizer(route_manager)
    base_position = (-49.2160678044742, -25.4233146347775)
    
    # Pontos de recarga estratégicos
    charging_points = [
        (-49.2733, -25.4284),      # Centro
        (-49.2336060009616, -25.4300625729625),  # Norte
        (-49.2047594214569, -25.4608672106041),  # Leste
        (-49.3400481020638, -25.4936598469491),  # Oeste
    ]
    
    # Divide pontos em 5 grupos
    points_per_day = len(route_manager.coordinates) // 5
    daily_points = [route_manager.coordinates[i:i + points_per_day] 
                   for i in range(0, len(route_manager.coordinates), points_per_day)]
    
    all_routes = []
    analysis_data = {}
    
    for day, points in enumerate(daily_points, 1):
        print(f"\nDia {day}: Otimizando {len(points)} pontos...")
        
        # Adiciona pontos de recarga aos pontos do dia
        day_points = points + charging_points
        
        ga = DroneGeneticAlgorithm(
            coordinates=day_points,
            base_position=base_position,
            population_size=50,    # Reduzido
            generations=20,        # Reduzido
            mutation_rate=0.2,     # Aumentado para mais diversidade
            elite_size=5
        )
        
        best_route, best_fitness = ga.optimize(verbose=False)  # Reduz logs
        all_routes.append(best_route)
        
        stats = simulate_day_route(best_route, base_position, day)
        analysis_data[str(day)] = stats
        
        print(f"✓ Rota otimizada: {len(best_route)} pontos, {stats['total_distance']:.1f}km")
    
    print("\nGerando visualização...")
    visualizer.create_map(all_routes, analysis_data)
    
    print("\n=== Sumário Final ===")
    total_distance = sum(data['total_distance'] for data in analysis_data.values())
    total_recharges = sum(data['recharge_count'] for data in analysis_data.values())
    print(f"Pontos visitados: {sum(len(route) for route in all_routes)}")
    print(f"Distância total: {total_distance:.1f}km")
    print(f"Recargas: {total_recharges}")

if __name__ == "__main__":
    main()