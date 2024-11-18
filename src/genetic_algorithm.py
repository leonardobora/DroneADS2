import random
import logging
from typing import List, Tuple
from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.route_visualizer import RouteVisualizer
from src.csv_writer import CSVWriter
from src.cep_mapper import CEPMapper

class DroneGeneticAlgorithm:
    def __init__(self, 
                 coordinates: List[Tuple[float, float]], 
                 base_position: Tuple[float, float],
                 cep_mapper: CEPMapper,
                 population_size: int = 100,
                 generations: int = 1000,
                 mutation_rate: float = 0.2,
                 elite_size: int = 10):
        """
        Inicializa o algoritmo genético para otimização de rotas do drone.
        
        :param coordinates: Lista de coordenadas a serem visitadas
        :param base_position: Posição inicial/final do drone
        :param population_size: Tamanho da população
        :param generations: Número de gerações
        :param mutation_rate: Taxa de mutação (0-1)
        :param elite_size: Número de melhores indivíduos a preservar
        """
        self.coordinates = coordinates
        self.base_position = base_position
        self.population_size = population_size
        self.generations = generations
        self.cep_mapper = cep_mapper
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        
        # Componentes para simulação
        self.weather = Weather()
        self.navigation = Navigation()
        
        logging.info(f"Coordenadas recebidas pelo algoritmo genético: {self.coordinates}")
    
    def create_individual(self) -> List[Tuple[float, float]]:
        """Cria um indivíduo (rota) aleatório, começando e terminando na base."""
        logging.info(f"Coordenadas recebidas para criar indivíduo: {self.coordinates}")
        if len(self.coordinates) < 2:
            raise ValueError("A lista de coordenadas deve conter pelo menos 2 pontos para criar um indivíduo.")
        route = random.sample(self.coordinates, len(self.coordinates))
        return [self.base_position] + route + [self.base_position]
    
    def calculate_fitness(self, route: List[Tuple[float, float]]) -> float:
        """Calcula fitness considerando todos os requisitos."""
        drone = Drone(self.base_position, Battery(100), Weather(), Navigation(), self.cep_mapper)
        total_cost = 0
        current_time = 6 * 3600  # 6h
        
        for i in range(len(route) - 1):
            current = route[i]
            next_point = route[i + 1]
            
            # Verifica horário
            if current_time > 19 * 3600:  # Após 19h
                return float('inf')
            
            # Verifica necessidade de recarga
            if not drone.can_reach(next_point):
                total_cost += 60  # Custo da recarga
                drone.remaining_autonomy = 28800
                current_time += 300  # +5min para recarga
            
            # Calcula custo do movimento
            distance = drone.navigation.calculate_distance(current, next_point)
            total_cost += distance * 10  # Peso para distância
            
            # Atualiza tempo
            flight_time = drone.calculate_flight_time(distance)
            current_time += flight_time + 60  # +1min para foto
        
        return total_cost
    
    def create_initial_population(self) -> List[List[Tuple[float, float]]]:
        """Cria a população inicial de rotas."""
        return [self.create_individual() for _ in range(self.population_size)]
    
    def select_parents(self, population: List[List[Tuple[float, float]]], 
                      fitness_scores: List[float]) -> List[List[Tuple[float, float]]]:
        """Seleciona pais para a próxima geração usando seleção por torneio."""
        selected = []
        for _ in range(self.population_size):
            # Seleciona 3 indivíduos aleatórios
            tournament = random.sample(list(enumerate(population)), 3)
            # Escolhe o melhor dos 3
            winner = min(tournament, key=lambda x: fitness_scores[x[0]])
            selected.append(winner[1])
        return selected 
    
    def crossover(self, parent1: List[Tuple[float, float]], 
                 parent2: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Realiza o crossover entre duas rotas (Order Crossover - OX)."""
        p1 = parent1[1:-1]
        p2 = parent2[1:-1]
        
        size = len(p1)
        child = [None] * size  # Inicializa child com None

        # Seleciona dois pontos de corte aleatórios
        start, end = sorted(random.sample(range(size), 2))
        
        # Copia a parte do primeiro pai para o filho
        for i in range(start, end):
            child[i] = p1[i]

        # Preenche o restante do filho com os genes do segundo pai
        remaining = [item for item in p2 if item not in child]
        
        j = 0
        for i in range(size):
            if child[i] is None:
                if j < len(remaining):  # Verifica se ainda há elementos em remaining
                    child[i] = remaining[j]
                    j += 1
                else:
                    child[i] = p1[j % len(p1)]  # Exemplo: repetir elementos de p1

        # Adiciona pontos base
        return [self.base_position] + child + [self.base_position]
    
    def mutate(self, route: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Realiza mutação na rota através de troca de dois pontos aleatórios."""
        if random.random() > self.mutation_rate:
            return route
        
        inner_route = route[1:-1]
        
        # Seleciona dois pontos aleatórios para trocar
        idx1, idx2 = random.sample(range(len(inner_route)), 2)
        inner_route[idx1], inner_route[idx2] = inner_route[idx2], inner_route[idx1]
        
        return [self.base_position] + inner_route + [self.base_position]
    
    def evolve(self, population: List[List[Tuple[float, float]]]) -> List[List[Tuple[float, float]]]:
        """Evolui a população para a próxima geração."""
        fitness_scores = [self.calculate_fitness(route) for route in population]
        
        # Preserva os melhores indivíduos (elitismo)
        elite = []
        if self.elite_size > 0:
            elite_idx = sorted(range(len(fitness_scores)), 
                             key=lambda k: fitness_scores[k])[:self.elite_size]
            elite = [population[i] for i in elite_idx]
        
        # Seleciona pais para reprodução
        parents = self.select_parents(population, fitness_scores)
        
        # Cria nova população através de crossover e mutação
        children = []
        while len(children) < (self.population_size - len(elite)):
            parent1, parent2 = random.sample(parents, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            children.append(child)
        
        # Retorna nova população (elite + filhos)
        return elite + children
    
    def optimize(self, max_generations: int = None, verbose: bool = True) -> Tuple[List[Tuple[float, float]], float]:
        """Executa o algoritmo genético e gera visualizações da evolução."""
        visualizer = RouteVisualizer(None)  # Apenas para visualização
        csv_writer = CSVWriter(self.cep_mapper)  # Para salvar resultados em CSV
        
        if max_generations is None:
            max_generations = self.generations
        
        population = self.create_initial_population()
        best_route = None
        best_fitness = float('inf')
        
        # Para cada geração
        for gen in range(max_generations):
            # Avalia população atual
            generation_data = []
            for route in population:
                fitness = self.calculate_fitness(route)
                generation_data.append((route, fitness))
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_route = route
                    if verbose:
                        logging.info(f"Nova melhor rota encontrada! Geração {gen}")
                        logging.info(f"Fitness: {best_fitness:.2f}")
            
            # Evolui para próxima geração
            population = self.evolve(population)
        
        # Salva a melhor rota final em CSV e HTML
        final_analysis = {
            'total_distance': best_fitness,
            'total_time': 0,
            'energy_consumption': 0,
            'wind_impact': 0
        }
        
        csv_writer.write_route('final_route.csv', [{
            'date': None,
            'departure_time': None,
            'arrival_time': None,
            'origin_coord': coord,
            'dest_coord': coord,
            'speed': 0,
            'landing': False
        } for coord in best_route])
        
        visualizer.create_map(
            routes=[best_route],
            analysis_data={'final': final_analysis},
            filename='final_route.html'
        )
        
        return best_route, best_fitness
    
    def calculate_recharge_cost(self, route, charging_points):
        return sum(1 for point in route if point in charging_points)