import random
from typing import List, Tuple, Callable
from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.route_visualizer import RouteVisualizer

class DroneGeneticAlgorithm:
    def __init__(self, 
                 coordinates: List[Tuple[float, float]], 
                 base_position: Tuple[float, float],
                 population_size: int = 100,
                 generations: int = 50,
                 mutation_rate: float = 0.1,
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
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        
        # Componentes para simulação
        self.weather = Weather()
        self.navigation = Navigation()
    
    def create_individual(self) -> List[Tuple[float, float]]:
        """
        Cria um indivíduo (rota) aleatório.
        Sempre começa e termina na base.
        """
        route = random.sample(self.coordinates, len(self.coordinates))
        return [self.base_position] + route + [self.base_position]
    
    def calculate_fitness(self, route: List[Tuple[float, float]]) -> float:
        """
        Calcula fitness considerando todos os requisitos:
        - Distância total
        - Janela de horário (6h-19h)
        - Recargas (R$60)
        - Impacto do vento
        - Tempo de parada para fotos
        """
        total_cost = 0
        drone = Drone(self.base_position, Battery(100), Weather(), Navigation())
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
        """
        Cria a população inicial de rotas.
        """
        return [self.create_individual() for _ in range(self.population_size)]
    
    def select_parents(self, population: List[List[Tuple[float, float]]], 
                      fitness_scores: List[float]) -> List[List[Tuple[float, float]]]:
        """
        Seleciona pais para a próxima geração usando seleção por torneio.
        """
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
        """
        Realiza o crossover entre duas rotas (Order Crossover - OX).
        Mantém a base como primeiro e último ponto.
        """
        # Remove pontos base para crossover
        p1 = parent1[1:-1]
        p2 = parent2[1:-1]
        
        size = len(p1)
        
        # Seleciona dois pontos de corte aleatórios
        start, end = sorted(random.sample(range(size), 2))
        
        # Cria filho com segmento do primeiro pai
        child = [None] * size
        for i in range(start, end + 1):
            child[i] = p1[i]
        
        # Preenche o resto com genes do segundo pai
        remaining = [x for x in p2 if x not in child[start:end+1]]
        j = 0
        for i in range(size):
            if child[i] is None:
                child[i] = remaining[j]
                j += 1
        
        # Adiciona pontos base
        return [self.base_position] + child + [self.base_position]
    
    def mutate(self, route: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Realiza mutação na rota através de troca de dois pontos aleatórios.
        Mantém a base como primeiro e último ponto.
        """
        if random.random() > self.mutation_rate:
            return route
        
        # Remove pontos base para mutação
        inner_route = route[1:-1]
        
        # Seleciona dois pontos aleatórios para trocar
        idx1, idx2 = random.sample(range(len(inner_route)), 2)
        inner_route[idx1], inner_route[idx2] = inner_route[idx2], inner_route[idx1]
        
        # Retorna rota com pontos base
        return [self.base_position] + inner_route + [self.base_position]
    
    def evolve(self, population: List[List[Tuple[float, float]]]) -> List[List[Tuple[float, float]]]:
        """
        Evolui a população para a próxima geração.
        """
        # Calcula fitness de toda a população
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
        """
        Executa o algoritmo genético e gera visualizações da evolução.
        """
        visualizer = RouteVisualizer(None)  # Apenas para visualização
        
        if max_generations is None:
            max_generations = self.generations
        
        population = self.create_initial_population()
        best_route = None
        best_fitness = float('inf')
        
        # Cria diretório evolution se não existir
        import os
        os.makedirs('evolution', exist_ok=True)
        
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
                        print(f"Nova melhor rota encontrada! Geração {gen}")
                        print(f"Fitness: {best_fitness:.2f}")
            
            # Gera visualização desta geração
            generation_data.sort(key=lambda x: x[1])  # Ordena por fitness
            top_5_routes = [route for route, _ in generation_data[:5]]  # 5 melhores rotas
            
            # Cria análise para esta geração
            gen_analysis = {
                str(gen+1): {
                    'total_distance': best_fitness,
                    'total_time': 0,
                    'energy_consumption': 0,
                    'wind_impact': 0
                }
            }
            
            # Salva mapa desta geração
            output_file = f'evolution/generation_{gen:03d}.html'
            visualizer.create_map(
                routes=top_5_routes,
                analysis_data=gen_analysis,
                filename=output_file
            )
            
            # Evolui para próxima geração
            population = self.evolve(population)
        
        return best_route, best_fitness