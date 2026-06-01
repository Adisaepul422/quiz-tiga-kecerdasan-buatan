from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from hill_climbing import HillClimbingSolver
from simulated_annealing import SimulatedAnnealingSolver
from genetic_algorithm import GeneticAlgorithmSolver
from utils import load_cvrp_data

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# ========== KONFIGURASI PATH ==========
# Dapatkan direktori backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Root direktori (simulasi-optimasi-logistik)
ROOT_DIR = os.path.dirname(BACKEND_DIR)
# Path ke data
DATA_PATH = os.path.join(ROOT_DIR, 'data', 'customers_cvrp.json')
# Path ke frontend
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

print(f"Backend dir: {BACKEND_DIR}")
print(f"Root dir: {ROOT_DIR}")
print(f"Data path: {DATA_PATH}")
print(f"Frontend dir: {FRONTEND_DIR}")

# Load data CVRP
try:
    cvrp_data = load_cvrp_data(DATA_PATH)
    print(f"Data loaded successfully. Customers: {cvrp_data['num_customers']}")
except Exception as e:
    print(f"Error loading data: {e}")
    cvrp_data = None

# ========== SERVING FRONTEND ==========
@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return f"Error: {e}", 500

@app.route('/style.css')
def serve_css():
    """Serve CSS file"""
    try:
        return send_from_directory(FRONTEND_DIR, 'style.css')
    except Exception as e:
        print(f"Error serving style.css: {e}")
        return f"Error: {e}", 500

@app.route('/app.js')
def serve_js():
    """Serve JavaScript file"""
    try:
        return send_from_directory(FRONTEND_DIR, 'app.js')
    except Exception as e:
        print(f"Error serving app.js: {e}")
        return f"Error: {e}", 500

# ========== HEALTH CHECK ==========
@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'ok', 'data_loaded': cvrp_data is not None})

# ========== API ENDPOINTS ==========
@app.route('/api/info', methods=['GET'])
def get_info():
    """Get problem information"""
    if cvrp_data is None:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    return jsonify({
        'success': True,
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
    if cvrp_data is None:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
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
    if cvrp_data is None:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
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
    if cvrp_data is None:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
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
    if cvrp_data is None:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
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
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)