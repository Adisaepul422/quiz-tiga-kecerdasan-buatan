from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from hill_climbing import HillClimbingSolver
from simulated_annealing import SimulatedAnnealingSolver
from genetic_algorithm import GeneticAlgorithmSolver
from utils import load_cvrp_data

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers_cvrp.json')
cvrp_data = load_cvrp_data(DATA_PATH)

# ========== SERVING FRONTEND ==========
@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/style.css')
def serve_css():
    """Serve CSS file"""
    return send_from_directory('../frontend', 'style.css')

@app.route('/app.js')
def serve_js():
    """Serve JavaScript file"""
    return send_from_directory('../frontend', 'app.js')

# ========== API ENDPOINTS ==========
@app.route('/api/info', methods=['GET'])
def get_info():
    """Get problem information"""
    return jsonify({
        'company_name': cvrp_data['company_name'],
        'product': cvrp_data['product'],
        'vehicle_capacity': cvrp_data['vehicle_capacity'],
        'num_customers': cvrp_data['num_customers'],
        'depot': cvrp_data['depot'],
        'customers': cvrp_data['customers']
    })

@app.route('/api/solve/hill-climbing', methods=['POST'])
def solve_hill_climbing():
    """Solve CVRP using Hill Climbing"""
    try:
        data = request.json
        max_iterations = data.get('max_iterations', 2000)
        variant = data.get('variant', 'simple')
        
        solver = HillClimbingSolver(cvrp_data)
        result = solver.solve(max_iterations, variant)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/solve/simulated-annealing', methods=['POST'])
def solve_simulated_annealing():
    """Solve CVRP using Simulated Annealing"""
    try:
        data = request.json
        initial_temp = data.get('initial_temp', 1000.0)
        cooling_rate = data.get('cooling_rate', 0.995)
        min_temp = data.get('min_temp', 0.01)
        iterations_per_temp = data.get('iterations_per_temp', 50)
        
        solver = SimulatedAnnealingSolver(cvrp_data)
        result = solver.solve(initial_temp, cooling_rate, min_temp, iterations_per_temp)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/solve/genetic-algorithm', methods=['POST'])
def solve_genetic_algorithm():
    """Solve CVRP using Genetic Algorithm"""
    try:
        data = request.json
        population_size = data.get('population_size', 80)
        generations = data.get('generations', 200)
        crossover_rate = data.get('crossover_rate', 0.85)
        mutation_rate = data.get('mutation_rate', 0.03)
        elitism_count = data.get('elitism_count', 2)
        
        solver = GeneticAlgorithmSolver(cvrp_data)
        result = solver.solve(population_size, generations, crossover_rate,
                             mutation_rate, elitism_count)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    """Compare all three algorithms"""
    try:
        results = {}
        
        # Hill Climbing (Simple)
        hc_solver = HillClimbingSolver(cvrp_data)
        hc_result = hc_solver.solve(1500, 'simple')
        results['hill_climbing'] = {
            'total_distance': hc_result['total_distance'],
            'num_routes': hc_result['num_routes'],
            'time': hc_result['time'],
            'iterations': hc_result['iterations']
        }
        
        # Simulated Annealing
        sa_solver = SimulatedAnnealingSolver(cvrp_data)
        sa_result = sa_solver.solve(800, 0.995, 0.01, 40)
        results['simulated_annealing'] = {
            'total_distance': sa_result['total_distance'],
            'num_routes': sa_result['num_routes'],
            'time': sa_result['time'],
            'iterations': sa_result['iterations']
        }
        
        # Genetic Algorithm
        ga_solver = GeneticAlgorithmSolver(cvrp_data)
        ga_result = ga_solver.solve(60, 150, 0.85, 0.03, 2)
        results['genetic_algorithm'] = {
            'total_distance': ga_result['total_distance'],
            'num_routes': ga_result['num_routes'],
            'time': ga_result['time'],
            'generations': ga_result['generations']
        }
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)