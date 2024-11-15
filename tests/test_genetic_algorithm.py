import unittest
from src.genetic_algorithm import DroneGeneticAlgorithm

class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        # Coordenadas de teste
        self.coordinates = [
            (-49.2336060009616, -25.4300625729625),
            (-49.2047594214569, -25.4608672106041),
            (-49.3400481020638, -25.4936598469491),
            (-49.2733, -25.4284)
        ]
        self.base = (-49.2160678044742, -25.4233146347775)
        
        self.ga = DroneGeneticAlgorithm(
            coordinates=self.coordinates,
            base_position=self.base,
            population_size=10,  # Menor para testes
            generations=5
        )
    
    def test_create_individual(self):
        route = self.ga.create_individual()
        
        # Verifica se começa e termina na base
        self.assertEqual(route[0], self.base)
        self.assertEqual(route[-1], self.base)
        
        # Verifica se todos os pontos estão presentes
        middle_points = route[1:-1]
        self.assertEqual(len(middle_points), len(self.coordinates))
        for coord in self.coordinates:
            self.assertIn(coord, middle_points)
    
    def test_calculate_fitness(self):
        route = self.ga.create_individual()
        fitness = self.ga.calculate_fitness(route)
        
        # Verifica se retorna um valor válido
        self.assertIsInstance(fitness, float)
        self.assertGreater(fitness, 0)
    
    def test_create_initial_population(self):
        population = self.ga.create_initial_population()
        
        # Verifica tamanho da população
        self.assertEqual(len(population), self.ga.population_size)
        
        # Verifica se todas as rotas são válidas
        for route in population:
            self.assertEqual(route[0], self.base)
            self.assertEqual(route[-1], self.base)
            self.assertEqual(len(route), len(self.coordinates) + 2)
    
    def test_crossover(self):
        parent1 = self.ga.create_individual()
        parent2 = self.ga.create_individual()
        
        child = self.ga.crossover(parent1, parent2)
        
        # Verifica se o filho é válido
        self.assertEqual(child[0], self.base)
        self.assertEqual(child[-1], self.base)
        self.assertEqual(len(child), len(parent1))
        
        # Verifica se todos os pontos estão presentes
        middle_points = child[1:-1]
        for coord in self.coordinates:
            self.assertIn(coord, middle_points)
    
    def test_mutate(self):
        route = self.ga.create_individual()
        mutated = self.ga.mutate(route)
        
        # Verifica se mantém pontos base
        self.assertEqual(mutated[0], self.base)
        self.assertEqual(mutated[-1], self.base)
        
        # Verifica se todos os pontos ainda estão presentes
        self.assertEqual(sorted(route), sorted(mutated))
    
    def test_optimize(self):
        # Testa otimização com poucas gerações
        best_route, best_fitness = self.ga.optimize(max_generations=5)
        
        # Verifica se retornou uma rota válida
        self.assertIsNotNone(best_route)
        self.assertEqual(best_route[0], self.base)
        self.assertEqual(best_route[-1], self.base)
        
        # Verifica se o fitness é válido
        self.assertIsInstance(best_fitness, float)
        self.assertGreater(best_fitness, 0)

if __name__ == '__main__':
    unittest.main() 