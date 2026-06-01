// API Configuration
const API_BASE_URL = '';

// Global variables
let convergenceChart = null;
let temperatureChart = null;
let currentAlgorithm = 'hc';
let problemInfo = null;

// Initialize page
async function initPage() {
    await loadProblemInfo();
    initChart();
    setupEventListeners();
}

// Load problem information
async function loadProblemInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/info`);
        problemInfo = await response.json();
        
        document.getElementById('capacity-display').innerHTML = `${problemInfo.vehicle_capacity} box`;
        document.getElementById('customers-display').innerHTML = problemInfo.num_customers;
        
        const totalDemand = problemInfo.customers.reduce((sum, c) => sum + c.demand, 0);
        document.getElementById('total-demand-display').innerHTML = `${totalDemand} box`;
    } catch (error) {
        console.error('Error loading problem info:', error);
        document.getElementById('status').innerHTML = '❌ Gagal terhubung ke server. Pastikan backend berjalan.';
    }
}

// Initialize chart
function initChart() {
    const ctx = document.getElementById('convergence-chart').getContext('2d');
    convergenceChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Total Jarak (km)',
                data: [],
                borderColor: '#2d5a3b',
                backgroundColor: 'rgba(45, 90, 59, 0.1)',
                tension: 0.3,
                fill: true,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'top' },
                title: { display: true, text: '📈 Kurva Konvergensi Algoritma' }
            },
            scales: {
                y: { title: { display: true, text: 'Jarak (km)' } },
                x: { title: { display: true, text: 'Iterasi / Generasi' } }
            }
        }
    });
}

// Update convergence chart
function updateChart(data, label) {
    if (!convergenceChart) return;
    convergenceChart.data.datasets = [{
        label: label,
        data: data,
        borderColor: '#2d5a3b',
        backgroundColor: 'rgba(45, 90, 59, 0.1)',
        tension: 0.3,
        fill: true,
        borderWidth: 2
    }];
    convergenceChart.update();
}

// Update temperature chart
function updateTemperatureChart(data) {
    const container = document.getElementById('temperature-chart-container');
    container.style.display = 'block';
    
    const ctx = document.getElementById('temperature-chart').getContext('2d');
    if (temperatureChart) temperatureChart.destroy();
    
    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Suhu (Temperature)',
                data: data,
                borderColor: '#f0b429',
                backgroundColor: 'rgba(240, 180, 41, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: { display: true, text: '🌡️ Cooling Schedule' }
            }
        }
    });
}

// Display routes
function displayRoutes(routesInfo) {
    const routesDiv = document.getElementById('routes-display');
    if (!routesInfo || routesInfo.length === 0) {
        routesDiv.innerHTML = 'Tidak ada rute yang ditemukan';
        return;
    }
    
    let html = '';
    routesInfo.forEach(route => {
        html += `<div style="margin-bottom: 12px; padding: 8px; background: #f0f4f0; border-radius: 8px;">
                    <strong>🚚 Rute ${route.route_number}</strong> (${route.demand} box, ${route.distance} km)<br>
                    <span style="font-size: 0.75rem;">🏭 Gudang → ${route.customers.join(' → ')} → 🏭</span>
                 </div>`;
    });
    routesDiv.innerHTML = html;
}

// Hill Climbing API call
async function solveHillClimbing() {
    const params = {
        max_iterations: parseInt(document.getElementById('hc-iterations').value),
        variant: document.getElementById('hc-variant').value
    };
    
    const response = await fetch(`${API_BASE_URL}/solve/hill-climbing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    });
    return await response.json();
}

// Simulated Annealing API call
async function solveSimulatedAnnealing() {
    const params = {
        initial_temp: parseFloat(document.getElementById('sa-init-temp').value),
        cooling_rate: parseFloat(document.getElementById('sa-cooling-rate').value),
        min_temp: parseFloat(document.getElementById('sa-min-temp').value),
        iterations_per_temp: 50
    };
    
    const response = await fetch(`${API_BASE_URL}/solve/simulated-annealing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    });
    return await response.json();
}

// Genetic Algorithm API call
async function solveGeneticAlgorithm() {
    const params = {
        population_size: parseInt(document.getElementById('ga-pop-size').value),
        generations: parseInt(document.getElementById('ga-generations').value),
        crossover_rate: parseFloat(document.getElementById('ga-crossover').value),
        mutation_rate: parseFloat(document.getElementById('ga-mutation').value),
        elitism_count: 2
    };
    
    const response = await fetch(`${API_BASE_URL}/solve/genetic-algorithm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    });
    return await response.json();
}

// Compare algorithms
async function compareAlgorithms() {
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = '🔄 Membandingkan semua algoritma... Mohon tunggu.';
    
    try {
        const response = await fetch(`${API_BASE_URL}/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        
        if (result.success) {
            const r = result.results;
            let html = '📊 <strong>Hasil Perbandingan:</strong><br>';
            html += `⛰️ Hill Climbing: ${r.hill_climbing.total_distance} km (${r.hill_climbing.time}s)<br>`;
            html += `🔥 Simulated Annealing: ${r.simulated_annealing.total_distance} km (${r.simulated_annealing.time}s)<br>`;
            html += `🧬 Genetic Algorithm: ${r.genetic_algorithm.total_distance} km (${r.genetic_algorithm.time}s)<br>`;
            html += '<span style="font-size: 0.75rem;">✨ Algoritma dengan jarak terpendek adalah yang terbaik!</span>';
            statusDiv.innerHTML = html;
        }
    } catch (error) {
        statusDiv.innerHTML = '❌ Gagal membandingkan algoritma. Pastikan backend berjalan.';
    }
}

// Main solve function
async function solve() {
    const solveBtn = document.getElementById('solve-btn');
    const statusDiv = document.getElementById('status');
    
    solveBtn.disabled = true;
    solveBtn.textContent = '⏳ Memproses...';
    statusDiv.innerHTML = '🔄 Menjalankan optimasi...';
    
    document.getElementById('temperature-chart-container').style.display = 'none';
    
    try {
        let result;
        
        switch(currentAlgorithm) {
            case 'hc':
                result = await solveHillClimbing();
                if (result.success) {
                    displayRoutes(result.routes_info);
                    document.getElementById('distance-display').innerHTML = `${result.total_distance} km`;
                    document.getElementById('time-display').innerHTML = `${result.time} detik`;
                    
                    const historyData = result.history.map(h => h.distance);
                    updateChart(historyData, `Hill Climbing (${result.variant})`);
                    statusDiv.innerHTML = `✅ Hill Climbing selesai! Jarak terpendek: ${result.total_distance} km dengan ${result.num_routes} rute.`;
                }
                break;
                
            case 'sa':
                result = await solveSimulatedAnnealing();
                if (result.success) {
                    displayRoutes(result.routes_info);
                    document.getElementById('distance-display').innerHTML = `${result.total_distance} km`;
                    document.getElementById('time-display').innerHTML = `${result.time} detik`;
                    
                    const historyData = result.history.map(h => h.distance);
                    updateChart(historyData, 'Simulated Annealing');
                    
                    if (result.temperature_history) {
                        const tempData = result.temperature_history.map(t => ({x: t.iteration, y: t.temperature}));
                        updateTemperatureChart(tempData);
                    }
                    
                    const acceptedCount = result.acceptance_history?.length || 0;
                    statusDiv.innerHTML = `✅ Simulated Annealing selesai! Jarak terpendek: ${result.total_distance} km. Menerima ${acceptedCount} solusi lebih buruk.`;
                }
                break;
                
            case 'ga':
                result = await solveGeneticAlgorithm();
                if (result.success) {
                    displayRoutes(result.routes_info);
                    document.getElementById('distance-display').innerHTML = `${result.total_distance} km`;
                    document.getElementById('time-display').innerHTML = `${result.time} detik`;
                    
                    const bestDistances = result.best_fitness_history.map(f => 1/f * 1000);
                    updateChart(bestDistances, 'Genetic Algorithm - Best Distance');
                    statusDiv.innerHTML = `✅ Genetic Algorithm selesai! Jarak terpendek: ${result.total_distance} km setelah ${result.generations} generasi.`;
                }
                break;
        }
        
        if (result && !result.success) {
            statusDiv.innerHTML = `❌ Error: ${result.error}`;
        }
        
    } catch (error) {
        console.error('Error:', error);
        statusDiv.innerHTML = '❌ Gagal terhubung ke backend. Pastikan server Flask berjalan di port 5000.';
    } finally {
        solveBtn.disabled = false;
        solveBtn.textContent = '▶️ Mulai Optimasi';
    }
}

// Setup event listeners
function setupEventListeners() {
    document.querySelectorAll('.algo-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.algo-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAlgorithm = btn.dataset.algo;
            
            document.getElementById('hc-params').classList.remove('active');
            document.getElementById('sa-params').classList.remove('active');
            document.getElementById('ga-params').classList.remove('active');
            
            if (currentAlgorithm === 'hc') document.getElementById('hc-params').classList.add('active');
            else if (currentAlgorithm === 'sa') document.getElementById('sa-params').classList.add('active');
            else if (currentAlgorithm === 'ga') document.getElementById('ga-params').classList.add('active');
        });
    });
    
    document.getElementById('solve-btn').addEventListener('click', solve);
    document.getElementById('compare-btn').addEventListener('click', compareAlgorithms);
}

// Start the app
document.addEventListener('DOMContentLoaded', initPage);