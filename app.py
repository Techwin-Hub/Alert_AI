import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime
import random
import uuid # For generating unique filenames

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model paths (placeholders)
MODEL_PATHS = {
    'ppe-detection': 'ppe_models/best.pt',
    'fire-smoke': 'fire_models/best.pt',
    'weapon-detection': 'weapon_models/best.pt'
}

# Create placeholder model files and their directories if they don't exist
for model_id, model_path in MODEL_PATHS.items():
    model_dir = os.path.dirname(model_path)
    if model_dir and not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
    if not os.path.exists(model_path):
        with open(model_path, 'w') as f:
            f.write(f"This is a placeholder model file for {model_id}.")

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/detect/<module_id>', methods=['POST'])
def detect_objects(module_id):
    if module_id not in MODEL_PATHS:
        return jsonify({'error': 'Invalid module ID'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Create a unique filename to prevent overwrites and for security
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # --- Placeholder for Model Inference ---
        # model_path_for_module = MODEL_PATHS[module_id]
        # For example, using a dummy processing step:
        # results = run_model_inference(filepath, model_path_for_module)
        # For now, simulate results:

        detections = []
        if module_id == 'ppe-detection':
            detections = [
                {'label': 'Helmet', 'confidence': random.uniform(0.7, 0.99), 'box': [10, 20, 50, 60]},
                {'label': 'Vest', 'confidence': random.uniform(0.6, 0.95), 'box': [70, 80, 120, 150]}
            ]
        elif module_id == 'fire-smoke':
            detections = [
                {'label': 'Smoke', 'confidence': random.uniform(0.75, 0.98), 'box': [30, 40, 80, 100]}
            ]
        elif module_id == 'weapon-detection':
             detections = [
                {'label': 'Handgun', 'confidence': random.uniform(0.8, 0.99), 'box': [50, 50, 100, 100]}
            ]

        # In a real app, you'd process the image (e.g., draw bounding boxes),
        # save a new version with detections, and return its URL.
        # For this example, we'll just return the URL of the *original* uploaded file.
        processed_image_url = f'/uploads/{unique_filename}'

        return jsonify({
            'message': 'File processed successfully',
            'filename': unique_filename,
            'module_id': module_id,
            'timestamp': datetime.now().isoformat(),
            'detections': detections,
            'image_url': processed_image_url
        })
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)