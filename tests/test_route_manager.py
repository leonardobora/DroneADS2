import unittest
from src.route_manager import RouteManager
from src.navigation import Navigation

class TestRouteManager(unittest.TestCase):
    def setUp(self):
        self.route_manager = RouteManager('data/coordenadas.csv')
        self.navigation = Navigation()
        
    def test_load_coordinates(self):
        # Testa carregamento inicial
        route_manager = RouteManager('data/coordenadas.csv')
        self.assertGreater(len(route_manager.load_points()), 0)
        
        # Testa carregamento com limite
        route_manager = RouteManager('data/coordenadas.csv', limit=5)
        route_manager.coordinates = []  # Limpa coordenadas existentes
        route_manager.load_points()
        self.assertEqual(len(route_manager.coordinates), 5)  # Verifica se o limite foi respeitado

    def test_plan_simple_route(self):
        # Ponto inicial (usando primeira coordenada do arquivo)
        start = (-49.2160678044742, -25.4233146347775)  # CEP: 82821020
        
        # Planeja rota com autonomia de 30 minutos (1800 segundos)
        route = self.route_manager.plan_route(start, autonomy=1800)
        
        # Verifica se a rota tem 4 pontos (inicial + 3 mais próximos)
        self.assertEqual(len(route), 4)
        
        # Verifica se o primeiro ponto é o inicial
        self.assertEqual(route[0], start)
        
        # Verifica se as distâncias são crescentes
        distances = []
        for i in range(1, len(route)):
            dist = self.navigation.calculate_distance(start, route[i])
            distances.append(dist)
        
        # Verifica se as distâncias estão em ordem crescente
        self.assertEqual(distances, sorted(distances))
        
        # Verifica se todas as distâncias são menores que 15km
        for dist in distances:
            self.assertLess(dist, 15)

    def test_optimized_route(self):
        # Carrega apenas 10 coordenadas para teste
        route_manager = RouteManager('data/coordenadas.csv', limit=10)
        route_manager.load_points()
        
        # Ponto inicial
        start = (-49.2160678044742, -25.4233146347775)
        
        # Planeja rota otimizada
        route = route_manager.plan_optimized_route(start, autonomy=7200, max_points=5)
        
        # Verificações básicas
        self.assertGreater(len(route), 1)
        self.assertEqual(route[0], start)
        
        # Verifica se a rota é factível
        from src.drone import Drone
        from src.battery import Battery
        from src.weather import Weather
        from src.navigation import Navigation
        
        drone = Drone(start, Battery(100), Weather(), Navigation())
        drone.remaining_autonomy = 7200
        
        # Tenta executar a rota
        for next_point in route[1:]:
            success = drone.move_to(next_point)
            self.assertTrue(success, f"Não foi possível mover para {next_point}")

    def test_find_charging_points(self):
        # Carrega coordenadas limitadas para teste
        route_manager = RouteManager('data/coordenadas.csv', limit=10)
        route_manager.load_points()
        
        # Define posição atual e autonomia limitada
        current_position = (-49.2160678044742, -25.4233146347775)  # CEP base
        remaining_autonomy = 1800  # 30 minutos
        
        # Encontra pontos de recarga alcançáveis
        reachable_points = route_manager.find_charging_points(current_position, remaining_autonomy)
        
        # Verificações
        self.assertGreater(len(reachable_points), 0, "Deve encontrar pelo menos um ponto de recarga")
        
        # Verifica se todos os pontos são realmente alcançáveis
        from src.drone import Drone
        from src.battery import Battery
        from src.weather import Weather
        from src.navigation import Navigation
        
        drone = Drone(current_position, Battery(100), Weather(), Navigation())
        drone.remaining_autonomy = remaining_autonomy
        
        for point in reachable_points:
            self.assertTrue(
                drone.can_reach(point),
                f"Ponto {point} foi marcado como alcançável mas não é"
            )
            
            # Calcula e verifica distância
            distance = drone.navigation.calculate_distance(current_position, point)
            self.assertLessEqual(
                distance, remaining_autonomy / 360,  # Considera autonomia em km
                f"Ponto de recarga muito distante: {distance:.2f}km"
            )

    def test_plan_multi_day_route(self):
        # Testa o planejamento de rotas para múltiplos dias
        base_position = (-49.2160678044742, -25.4233146347775)
        daily_routes = self.route_manager.plan_multi_day_route(base_position, days=5, autonomy=1800)
        
        # Verifica se as rotas foram planejadas corretamente
        self.assertEqual(len(daily_routes), 5, "Deve haver uma rota para cada dia")
        
        for route in daily_routes:
            self.assertGreater(len(route), 0, "Cada rota deve ter pelo menos um ponto")
            self.assertEqual(route[0], base_position, "A rota deve começar na base")

if __name__ == '__main__':
    unittest.main() 