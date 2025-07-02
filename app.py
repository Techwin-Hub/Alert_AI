import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime
import random
import uuid # For generating unique filenames
from ultralytics import YOLO
from PIL import Image

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
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Load model
        model = YOLO(MODEL_PATHS[module_id])
        detections = []
        is_video = ext in ['mp4', 'avi', 'mov']

        if is_video:
            # --- Video Handling ---
            import cv2

            cap = cv2.VideoCapture(filepath)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            result_filename = unique_filename.replace('.', '_result.')
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model(frame)[0]

                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    detections.append({
                        'label': label,
                        'confidence': conf,
                        'box': [x1, y1, x2, y2]
                    })

                out.write(frame)

            cap.release()
            out.release()
            processed_image_url = f'/uploads/{os.path.basename(result_path)}'

        else:
            # --- Image Handling ---
            results = model(filepath)
            result_img_path = filepath.replace('.', '_result.')
            results[0].save(filename=result_img_path)
            processed_image_url = f'/uploads/{os.path.basename(result_img_path)}'

            for box in results[0].boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                detections.append({
                    'label': label,
                    'confidence': float(box.conf[0]),
                    'box': box.xyxy[0].tolist()
                })

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

if __name__ == "__main__":
    app.run(debug=True)
