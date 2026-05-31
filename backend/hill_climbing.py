import time
import random
import math
from utils import (
    get_random_route_sequence, get_neighbor_sequence, get_two_opt_neighbor,
    split_into_routes, fitness_function, calculate_routes_distance, calculate_route_distance
)

class HillClimbingSolver:
    def __init__(self, data):
        self.data = data
        self.num_customers = data['num_customers']
        self.distance_matrix = data['distance_matrix']
        self.demands = data['demands']
        self.capacity = data['vehicle_capacity']
    
    def solve(self, max_iterations=2000, variant='simple', max_stagnation=200):
        """
        Solve CVRP using Hill Climbing algorithm
        
        Args:
            max_iterations: Maximum number of iterations
            variant: 'simple', 'steepest', or 'stochastic'
            max_stagnation: Stop if no improvement for this many iterations
        
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
        
        history = [{'iteration': 0, 'distance': current_fitness}]
        stagnation_count = 0
        
        for i in range(max_iterations):
            if variant == 'simple':
                # Simple Hill Climbing: try one random neighbor
                neighbor_seq = get_neighbor_sequence(current_sequence)
                neighbor_routes = split_into_routes(neighbor_seq, self.demands, self.capacity)
                neighbor_fitness = fitness_function(neighbor_routes, self.distance_matrix,
                                                    self.demands, self.capacity)
                
                if neighbor_fitness < current_fitness:
                    current_sequence = neighbor_seq
                    current_routes = neighbor_routes
                    current_fitness = neighbor_fitness
                    stagnation_count = 0
                    history.append({'iteration': i+1, 'distance': current_fitness})
                else:
                    stagnation_count += 1
            
            elif variant == 'steepest':
                # Steepest-Ascent: try multiple neighbors, pick best
                best_neighbor_seq = None
                best_neighbor_fitness = current_fitness
                
                # Try 30 random neighbors
                for _ in range(30):
                    neighbor_seq = get_neighbor_sequence(current_sequence)
                    neighbor_routes = split_into_routes(neighbor_seq, self.demands, self.capacity)
                    neighbor_fitness = fitness_function(neighbor_routes, self.distance_matrix,
                                                        self.demands, self.capacity)
                    
                    if neighbor_fitness < best_neighbor_fitness:
                        best_neighbor_fitness = neighbor_fitness
                        best_neighbor_seq = neighbor_seq
                
                if best_neighbor_seq and best_neighbor_fitness < current_fitness:
                    current_sequence = best_neighbor_seq
                    current_routes = split_into_routes(best_neighbor_seq, self.demands, self.capacity)
                    current_fitness = best_neighbor_fitness
                    stagnation_count = 0
                    history.append({'iteration': i+1, 'distance': current_fitness})
                else:
                    stagnation_count += 1
            
            elif variant == 'stochastic':
                # Stochastic Hill Climbing with probabilistic acceptance
                neighbor_seq = get_two_opt_neighbor(current_sequence)
                neighbor_routes = split_into_routes(neighbor_seq, self.demands, self.capacity)
                neighbor_fitness = fitness_function(neighbor_routes, self.distance_matrix,
                                                    self.demands, self.capacity)
                
                delta = neighbor_fitness - current_fitness
                
                if delta < 0:
                    # Accept better solution
                    current_sequence = neighbor_seq
                    current_routes = neighbor_routes
                    current_fitness = neighbor_fitness
                    history.append({'iteration': i+1, 'distance': current_fitness})
                else:
                    # Accept worse solution with decreasing probability
                    temperature = 1.0 - (i / max_iterations)
                    acceptance_prob = math.exp(-delta / (current_fitness * temperature + 1))
                    
                    if random.random() < acceptance_prob:
                        current_sequence = neighbor_seq
                        current_routes = neighbor_routes
                        current_fitness = neighbor_fitness
                        history.append({'iteration': i+1, 'distance': current_fitness})
                    else:
                        stagnation_count += 1
            
            # Update global best
            if current_fitness < best_fitness:
                best_fitness = current_fitness
                best_sequence = current_sequence.copy()
                best_routes = current_routes.copy()
            
            # Check stagnation
            if stagnation_count >= max_stagnation:
                break
        
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
            'iterations': i + 1,
            'history': history,
            'time': round(execution_time, 3),
            'variant': variant
        }