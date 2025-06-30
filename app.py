from flask import Flask, render_template, jsonify
from datetime import datetime
import random

app = Flask(__name__)

# Surveillance modules data
SURVEILLANCE_MODULES = [
    {
        'id': 'face-detection',
        'title': 'Face Detection + Anti-Spoofing',
        'icon': 'fa-user-shield',
        'description': 'Real-time face recognition with liveness detection',
        'status': 'safe',
        'alert_count': 0
    },
    {
        'id': 'ppe-detection',
        'title': 'PPE Detection',
        'icon': 'fa-hard-hat',
        'description': 'Helmets, Safety Vests, and Gloves monitoring',
        'status': 'warning',
        'alert_count': 2
    },
    {
        'id': 'weapon-detection',
        'title': 'Weapon Detection',
        'icon': 'fa-shield-alt',
        'description': 'Automatic weapon and threat identification',
        'status': 'safe',
        'alert_count': 0
    },
    {
        'id': 'restricted-area',
        'title': 'Restricted Area Intrusion',
        'icon': 'fa-exclamation-triangle',
        'description': 'Unauthorized access detection',
        'status': 'alert',
        'alert_count': 1
    },
    {
        'id': 'fire-smoke',
        'title': 'Fire/Smoke Detection',
        'icon': 'fa-fire',
        'description': 'Early fire and smoke detection system',
        'status': 'warning',
        'alert_count': 3
    }
]

@app.route('/')
def dashboard():
    """Main dashboard route"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('dashboard.html', modules=SURVEILLANCE_MODULES, last_update=now)

@app.route('/api/status')
def get_status():
    """API endpoint to get updated status for all modules"""
    updated_modules = []
    
    for module in SURVEILLANCE_MODULES:
        # Simulate random status changes
        statuses = ['safe', 'warning', 'alert']
        weights = [0.7, 0.2, 0.1]  # Higher probability for safe status
        
        new_status = random.choices(statuses, weights=weights)[0]
        
        # Update alert count based on status
        if new_status == 'alert':
            alert_count = random.randint(1, 5)
        elif new_status == 'warning':
            alert_count = random.randint(0, 2)
        else:
            alert_count = 0
            
        updated_module = module.copy()
        updated_module['status'] = new_status
        updated_module['alert_count'] = alert_count
        updated_module['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        updated_modules.append(updated_module)
    
    return jsonify(updated_modules)

@app.route('/module/<module_id>')
def module_detail(module_id):
    """Individual module detail page"""
    module = next((m for m in SURVEILLANCE_MODULES if m['id'] == module_id), None)
    if not module:
        return "Module not found", 404
    
    return render_template('module_detail.html', module=module)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)