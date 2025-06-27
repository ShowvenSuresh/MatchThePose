from flask import Flask, render_template, Response, jsonify, request, session
import cv2
import os
import random
import json
from app.utils.camera import VideoCamera

app = Flask(__name__)
app.secret_key = 'pose-matcher-secret-key-2025'  # Change this to a secure secret key

# Initialize camera globally
camera = None

def get_camera():
    global camera
    if camera is None:
        camera = VideoCamera()
    return camera

@app.route('/')
def index():
    return render_template('page1.html')

@app.route('/game')
def game():
    # Initialize game session
    session['score'] = 0
    session['round'] = 0
    session['max_rounds'] = 10
    
    # Get all pose classes from static/poses directory
    poses_dir = os.path.join(app.static_folder, 'poses')
    pose_classes = [d for d in os.listdir(poses_dir) if os.path.isdir(os.path.join(poses_dir, d))]
    
    # Generate random sequence of 10 poses (can repeat)
    pose_sequence = []
    for _ in range(10):
        pose_class = random.choice(pose_classes)
        # Get random image from this pose class
        pose_images_dir = os.path.join(poses_dir, pose_class)
        images = [f for f in os.listdir(pose_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            image = random.choice(images)
            pose_sequence.append({
                'class': pose_class,
                'image': f'poses/{pose_class}/{image}'
            })
    
    session['pose_sequence'] = pose_sequence
    session['current_pose_index'] = 0
    
    return render_template('page2.html')

@app.route('/get_current_pose')
def get_current_pose():
    if 'pose_sequence' not in session or 'current_pose_index' not in session:
        return jsonify({'error': 'Game not initialized'})
    
    current_index = session['current_pose_index']
    pose_sequence = session['pose_sequence']
    
    if current_index >= len(pose_sequence):
        return jsonify({'game_over': True, 'final_score': session.get('score', 0)})
    
    current_pose = pose_sequence[current_index]
    return jsonify({
        'pose_class': current_pose['class'],
        'image_path': current_pose['image'],
        'round': current_index + 1,
        'total_rounds': session['max_rounds'],
        'score': session.get('score', 0)
    })

@app.route('/check_pose')
def check_pose():
    if 'pose_sequence' not in session or 'current_pose_index' not in session:
        return jsonify({'error': 'Game not initialized'})
    
    current_index = session['current_pose_index']
    pose_sequence = session['pose_sequence']
    
    if current_index >= len(pose_sequence):
        return jsonify({'game_over': True, 'final_score': session.get('score', 0)})
    
    # Get the current pose prediction from camera
    camera = get_camera()
    current_prediction = getattr(camera, 'last_prediction', 'No pose detected')
    expected_pose = pose_sequence[current_index]['class']
    
    # Check if poses match (normalize names for comparison)
    predicted_normalized = current_prediction.replace('_', ' ').replace('-', ' ').lower().strip()
    expected_normalized = expected_pose.replace('_', ' ').replace('-', ' ').lower().strip()
    
    is_correct = predicted_normalized == expected_normalized
    
    if is_correct:
        session['score'] = session.get('score', 0) + 5
    
    return jsonify({
        'correct': is_correct,
        'predicted_pose': current_prediction,
        'expected_pose': expected_pose,
        'score': session.get('score', 0)
    })

@app.route('/next_pose')
def next_pose():
    if 'current_pose_index' not in session:
        return jsonify({'error': 'Game not initialized'})
    
    session['current_pose_index'] = session.get('current_pose_index', 0) + 1
    
    if session['current_pose_index'] >= session.get('max_rounds', 10):
        return jsonify({'game_over': True, 'final_score': session.get('score', 0)})
    
    return jsonify({'success': True})

@app.route('/video_feed')
def video_feed():
    def generate():
        camera = get_camera()
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_pose_prediction')
def get_pose_prediction():
    camera = get_camera()
    prediction = getattr(camera, 'last_prediction', 'No pose detected')
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)
