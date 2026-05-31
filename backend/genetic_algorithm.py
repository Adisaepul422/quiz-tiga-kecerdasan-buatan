import time
import random
import numpy as np
from utils import (
    get_random_route_sequence, split_into_routes, fitness_function, 
    calculate_routes_distance, get_two_opt_neighbor, calculate_route_distance
)

class GeneticAlgorithmSolver:
    def __init__(self, data):
        self.data = data
        self.num_customers = data['num_customers']
        self.distance_matrix = data['distance_matrix']
        self.demands = data['demands']
        self.capacity = data['vehicle_capacity']
    
    def create_individual(self):
        """Create a random customer sequence (chromosome)"""
        return get_random_route_sequence(self.num_customers)
    
    def calculate_fitness(self, sequence):
        """
        Calculate fitness for a sequence
        Higher fitness is better (inverse of total distance)
        """
        routes = split_into_routes(sequence, self.demands, self.capacity)
        total_cost = fitness_function(routes, self.distance_matrix, 
                                      self.demands, self.capacity)
        
        # Handle infeasible solutions
        if total_cost == float('inf'):
            return 0
        
        # Fitness = 1 / cost (minimization to maximization)
        return 1.0 / (total_cost + 1)
    
    def tournament_selection(self, population, fitnesses, tournament_size=3):
        """Select parent using tournament selection"""
        selected = []
        for _ in range(2):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitnesses[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            selected.append(population[winner_idx])
        return selected[0], selected[1]
    
    def ordered_crossover(self, parent1, parent2):
        """
        Order Crossover (OX) for TSP/CVRP
        Preserves relative order of customers from parents
        """
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        
        # Create child with -1 placeholders
        child = [-1] * size
        
        # Copy segment from parent1
        child[start:end+1] = parent1[start:end+1]
        
        # Fill remaining positions from parent2
        parent2_idx = 0
        for i in range(size):
            if child[i] == -1:
                while parent2[parent2_idx] in child:
                    parent2_idx += 1
                child[i] = parent2[parent2_idx]
                parent2_idx += 1
        
        return child
    
    def mutate(self, sequence, mutation_rate):
        """
        Swap mutation or 2-opt mutation
        """
        if random.random() < mutation_rate:
            # 50% chance of swap mutation, 50% chance of 2-opt
            if random.random() < 0.5:
                # Swap mutation
                idx1, idx2 = random.sample(range(len(sequence)), 2)
                sequence[idx1], sequence[idx2] = sequence[idx2], sequence[idx1]
            else:
                # 2-opt mutation
                i, j = sorted(random.sample(range(len(sequence)), 2))
                sequence[i:j+1] = reversed(sequence[i:j+1])
        return sequence
    
    def solve(self, population_size=80, generations=200, 
              crossover_rate=0.85, mutation_rate=0.03, elitism_count=2):
        """
        Solve CVRP using Genetic Algorithm
        
        Args:
            population_size: Number of individuals in population
            generations: Number of generations to evolve
            crossover_rate: Probability of crossover (0-1)
            mutation_rate: Probability of mutation (0-1)
            elitism_count: Number of best individuals to preserve
        
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        # Initialize population
        population = [self.create_individual() for _ in range(population_size)]
        
        best_fitness_history = []
        avg_fitness_history = []
        best_sequence = None
        best_fitness = 0
        best_cost = float('inf')
        
        for generation in range(generations):
            # Calculate fitness for all individuals
            fitnesses = [self.calculate_fitness(ind) for ind in population]
            
            # Track best and average fitness
            current_best_fitness = max(fitnesses)
            current_avg_fitness = sum(fitnesses) / len(fitnesses)
            best_fitness_history.append(current_best_fitness)
            avg_fitness_history.append(current_avg_fitness)
            
            # Update global best
            best_idx = fitnesses.index(current_best_fitness)
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_sequence = population[best_idx].copy()
                routes = split_into_routes(best_sequence, self.demands, self.capacity)
                best_cost = fitness_function(routes, self.distance_matrix,
                                            self.demands, self.capacity)
            
            # Elitism: preserve best individuals
            sorted_indices = sorted(range(len(fitnesses)), 
                                   key=lambda x: fitnesses[x], reverse=True)
            new_population = [population[idx].copy() 
                            for idx in sorted_indices[:elitism_count]]
            
            # Create new generation
            while len(new_population) < population_size:
                # Selection
                parent1, parent2 = self.tournament_selection(population, fitnesses)
                
                # Crossover
                if random.random() < crossover_rate:
                    child1 = self.ordered_crossover(parent1, parent2)
                    child2 = self.ordered_crossover(parent2, parent1)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                child1 = self.mutate(child1, mutation_rate)
                child2 = self.mutate(child2, mutation_rate)
                
                new_population.extend([child1, child2])
            
            # Trim excess individuals
            population = new_population[:population_size]
            
            # Adaptive mutation rate (increase if stagnation)
            if generation > 50 and generation % 50 == 0:
                if len(best_fitness_history) > 10:
                    recent_improvement = (best_fitness_history[-10] - best_fitness_history[-1])
                    if recent_improvement < 0.001:
                        mutation_rate = min(0.15, mutation_rate * 1.1)
        
        # Calculate final routes
        best_routes = split_into_routes(best_sequence, self.demands, self.capacity)
        total_distance = calculate_routes_distance(best_routes, self.distance_matrix)
        
        execution_time = time.time() - start_time
        
        # Build detailed route information
        routes_info = []
        for idx, route in enumerate(best_routes):
            route_cities = [self.data['customers'][c-1]['name'] if c > 0 else 'Gudang' 
                           for c in route]
            route_demand = sum(self.demands[c] for c in route)
            route_distance = calculate_route_distance(route, self.distance_matrix)
            
            routes_info.append({
                'route_number': idx + 1,
                'customers': route_cities,
                'customer_ids': route,
                'demand': route_demand,
                'distance': round(route_distance, 2)
            })
        
        return {
            'success': True,
            'best_sequence': best_sequence,
            'routes': best_routes,
            'routes_info': routes_info,
            'total_distance': round(total_distance, 2),
            'num_routes': len(best_routes),
            'generations': generations,
            'best_fitness_history': best_fitness_history,
            'avg_fitness_history': avg_fitness_history,
            'best_fitness': best_fitness,
            'best_cost': round(best_cost, 2),
            'time': round(execution_time, 3)
        }