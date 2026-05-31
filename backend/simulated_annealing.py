import time
import random
import math
from utils import (
    get_random_route_sequence, get_two_opt_neighbor,
    split_into_routes, fitness_function, calculate_routes_distance, calculate_route_distance
)

class SimulatedAnnealingSolver:
    def __init__(self, data):
        self.data = data
        self.num_customers = data['num_customers']
        self.distance_matrix = data['distance_matrix']
        self.demands = data['demands']
        self.capacity = data['vehicle_capacity']
    
    def solve(self, initial_temp=1000.0, cooling_rate=0.995, 
              min_temp=0.01, iterations_per_temp=50):
        """
        Solve CVRP using Simulated Annealing algorithm
        
        Args:
            initial_temp: Starting temperature
            cooling_rate: Rate at which temperature decreases (0.8-0.999)
            min_temp: Minimum temperature to stop
            iterations_per_temp: Number of iterations at each temperature
        
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        # Initialize random sequence
        current_sequence = get_random_route_sequence(self.num_customers)
        current_routes = split_into_routes(current_sequence, self.demands, self.capacity)
        current_fitness = fitness_function(current_routes, self.distance_matrix, 
                                           self.demands, self.capacity)
        
        best_sequence = current_sequence.copy()
        best_routes = current_routes.copy()
        best_fitness = current_fitness
        
        temperature = initial_temp
        history = []
        temperature_history = []
        acceptance_history = []
        
        iteration_count = 0
        
        while temperature > min_temp:
            for _ in range(iterations_per_temp):
                iteration_count += 1
                
                # Generate neighbor using 2-opt
                neighbor_seq = get_two_opt_neighbor(current_sequence)
                neighbor_routes = split_into_routes(neighbor_seq, self.demands, self.capacity)
                neighbor_fitness = fitness_function(neighbor_routes, self.distance_matrix,
                                                    self.demands, self.capacity)
                
                delta = neighbor_fitness - current_fitness
                
                # Acceptance criteria (Boltzmann)
                accepted = False
                if delta < 0:
                    # Accept better solution
                    current_sequence = neighbor_seq
                    current_routes = neighbor_routes
                    current_fitness = neighbor_fitness
                    accepted = True
                else:
                    # Accept worse solution with probability
                    acceptance_prob = math.exp(-delta / temperature)
                    if random.random() < acceptance_prob:
                        current_sequence = neighbor_seq
                        current_routes = neighbor_routes
                        current_fitness = neighbor_fitness
                        accepted = True
                        acceptance_history.append({
                            'iteration': iteration_count,
                            'delta': round(delta, 2),
                            'probability': round(acceptance_prob, 4),
                            'temperature': round(temperature, 2)
                        })
                
                # Update best solution
                if current_fitness < best_fitness:
                    best_fitness = current_fitness
                    best_sequence = current_sequence.copy()
                    best_routes = current_routes.copy()
                
                # Record history every 20 iterations
                if iteration_count % 20 == 0:
                    history.append({
                        'iteration': iteration_count, 
                        'distance': current_fitness,
                        'temperature': round(temperature, 2)
                    })
            
            # Cool down
            temperature *= cooling_rate
            temperature_history.append({
                'iteration': iteration_count, 
                'temperature': round(temperature, 2)
            })
        
        # Calculate total distance (without penalty)
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
            'iterations': iteration_count,
            'history': history,
            'temperature_history': temperature_history,
            'acceptance_history': acceptance_history,
            'time': round(execution_time, 3)
        }