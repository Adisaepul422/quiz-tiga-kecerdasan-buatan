import json
import math
import random
import numpy as np

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def load_cvrp_data(filepath):
    """Load CVRP data from JSON file"""
    import json
    import os
    
    # Jika file tidak ditemukan, coba cari di lokasi alternatif
    if not os.path.exists(filepath):
        # Coba di root/data/
        alt_path = os.path.join(os.path.dirname(os.path.dirname(filepath)), 'data', 'customers_cvrp.json')
        if os.path.exists(alt_path):
            filepath = alt_path
        else:
            raise FileNotFoundError(f"Data file not found at {filepath} or {alt_path}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    
    # Build distance matrix using Haversine formula
    all_locations = [data['depot']] + data['customers']
    num_points = len(all_locations)
    distance_matrix = np.zeros((num_points, num_points))
    
    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                dist = haversine_distance(
                    all_locations[i]['lat'], all_locations[i]['lng'],
                    all_locations[j]['lat'], all_locations[j]['lng']
                )
                distance_matrix[i][j] = round(dist, 2)
    
    # Build demands array (index 0 is depot with 0 demand)
    demands = [0] + [c['demand'] for c in data['customers']]
    
    return {
        'company_name': data['company_name'],
        'product': data['product'],
        'vehicle_capacity': data['vehicle_capacity'],
        'depot': data['depot'],
        'customers': data['customers'],
        'num_customers': len(data['customers']),
        'num_points': num_points,
        'distance_matrix': distance_matrix.tolist(),
        'demands': demands
    }

def calculate_route_distance(route, distance_matrix):
    """Calculate total distance of a route (without capacity check)"""
    if not route or len(route) < 2:
        return 0
    
    total = 0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i]][route[i+1]]
    
    # Return to depot (0)
    total += distance_matrix[route[-1]][0]
    
    return total

def calculate_routes_distance(routes, distance_matrix):
    """Calculate total distance of multiple routes"""
    total = 0
    for route in routes:
        total += calculate_route_distance(route, distance_matrix)
    return total

def check_route_capacity(route, demands, capacity):
    """Check if a single route respects vehicle capacity"""
    total_demand = sum(demands[node] for node in route)
    return total_demand <= capacity

def split_into_routes(sequence, demands, capacity):
    """
    Split a sequence of customers into multiple routes
    respecting vehicle capacity
    """
    routes = []
    current_route = []
    current_load = 0
    
    for customer in sequence:
        demand = demands[customer]
        
        # Check if adding this customer exceeds capacity
        if current_load + demand <= capacity:
            current_route.append(customer)
            current_load += demand
        else:
            # Start new route if current route not empty
            if current_route:
                routes.append(current_route)
            current_route = [customer]
            current_load = demand
    
    # Append last route
    if current_route:
        routes.append(current_route)
    
    return routes

def fitness_function(routes, distance_matrix, demands, capacity):
    """
    Calculate fitness (lower distance is better)
    Returns negative distance for maximization in GA
    """
    # Check if any route exceeds capacity
    for route in routes:
        if not check_route_capacity(route, demands, capacity):
            return float('inf')
    
    total_distance = calculate_routes_distance(routes, distance_matrix)
    
    # Penalty for number of routes (minimize number of vehicles)
    route_penalty = len(routes) * 5  # Small penalty per extra route
    
    return total_distance + route_penalty

def get_random_route_sequence(num_customers):
    """Generate random sequence of customers (1 to num_customers)"""
    sequence = list(range(1, num_customers + 1))
    random.shuffle(sequence)
    return sequence

def get_neighbor_sequence(sequence):
    """
    Generate neighbor sequence by swapping two random positions
    (2-opt style local move)
    """
    neighbor = sequence.copy()
    idx1, idx2 = random.sample(range(len(sequence)), 2)
    neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]
    return neighbor

def get_two_opt_neighbor(sequence):
    """
    Generate neighbor using 2-opt move (reverse segment)
    """
    neighbor = sequence.copy()
    size = len(neighbor)
    i, j = sorted(random.sample(range(size), 2))
    neighbor[i:j+1] = reversed(neighbor[i:j+1])
    return neighbor