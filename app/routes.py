from flask import Flask, render_template, Response, jsonify, request, session
import cv2
import os
import random
import json
from app.utils.camera import VideoCamera
from app.utils.telegram_bot import TelegramBot

app = Flask(__name__)
app.secret_key = 'pose-matcher-secret-key-2025'  # Change this to a secure secret key

# Initialize camera globally
camera = None

# Initialize Telegram bot
TELEGRAM_TOKEN = "7527324296:AAH12tnGbZi61aTHA0wg6i9uPO8SH3sDLw4"
telegram_bot = TelegramBot(TELEGRAM_TOKEN)

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
    
    # Generate random sequence of 10 poses (no consecutive duplicates, max 2 per pose)
    pose_sequence = []
    last_pose_class = None
    pose_usage_count = {}  # Track how many times each pose has been used
    max_usage_per_pose = 2
    
    for _ in range(10):
        # Get available pose classes (excluding the last one and those at max usage)
        available_poses = []
        for pose in pose_classes:
            # Skip if it's the same as last pose (no consecutive duplicates)
            if pose == last_pose_class:
                continue
            # Skip if this pose has already been used max times
            if pose_usage_count.get(pose, 0) >= max_usage_per_pose:
                continue
            available_poses.append(pose)
        
        # If no poses are available (shouldn't happen with 10 rounds and max 2 usage), 
        # allow any pose except the last one
        if not available_poses:
            available_poses = [pose for pose in pose_classes if pose != last_pose_class]
        
        # Select random pose from available ones
        pose_class = random.choice(available_poses)
        
        # Get random image from this pose class
        pose_images_dir = os.path.join(poses_dir, pose_class)
        images = [f for f in os.listdir(pose_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            image = random.choice(images)
            pose_sequence.append({
                'class': pose_class,
                'image': f'poses/{pose_class}/{image}'
            })
            # Update tracking
            last_pose_class = pose_class
            pose_usage_count[pose_class] = pose_usage_count.get(pose_class, 0) + 1
    
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
    
    # Set the expected pose in the camera for detection box color
    camera = get_camera()
    camera.set_expected_pose(current_pose['class'])
    
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
    
    # Get the current pose prediction with confidence from camera
    camera = get_camera()
    expected_pose = pose_sequence[current_index]['class']
    
    # Set the expected pose in the camera for detection box color
    camera.set_expected_pose(expected_pose)
    
    # Use the last prediction and confidence from the video feed
    # to avoid conflicts with the ongoing camera stream
    current_prediction = getattr(camera, 'last_prediction', 'No pose detected')
    confidence = getattr(camera, 'last_confidence', 0.0)
    
    # Check if poses match (normalize names for comparison)
    predicted_normalized = current_prediction.replace('_', ' ').replace('-', ' ').lower().strip()
    expected_normalized = expected_pose.replace('_', ' ').replace('-', ' ').lower().strip()
    
    is_correct = predicted_normalized == expected_normalized
    
    # Calculate score based on confidence percentage (only if pose is correct)
    score_to_add = 0
    if is_correct and confidence > 0:
        if confidence < 50:
            score_to_add = 1
        elif confidence < 60:
            score_to_add = 2
        elif confidence < 70:
            score_to_add = 3
        elif confidence < 80:
            score_to_add = 4
        else:  # confidence >= 80
            score_to_add = 5
    
    return jsonify({
        'correct': is_correct,
        'predicted_pose': current_prediction,
        'expected_pose': expected_pose,
        'confidence': confidence,
        'score_to_add': score_to_add,
        'score': session.get('score', 0)
    })

@app.route('/add_score', methods=['POST'])
def add_score():
    data = request.get_json()
    points = data.get('points', 0)
    
    current_score = session.get('score', 0)
    session['score'] = current_score + points
    
    return jsonify({
        'success': True,
        'score': session['score'],
        'points_added': points
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
    
    # Use the last prediction and confidence from the video feed
    # to avoid conflicts with the ongoing camera stream
    prediction = getattr(camera, 'last_prediction', 'No pose detected')
    confidence = getattr(camera, 'last_confidence', 0.0)
    
    return jsonify({
        'prediction': prediction,
        'confidence': confidence
    })

@app.route('/setup_telegram', methods=['POST'])
def setup_telegram():
    """Setup Telegram notifications for the user"""
    data = request.get_json()
    phone_number = data.get('phone_number', '').strip()
    
    if not phone_number:
        return jsonify({'success': False, 'error': 'Phone number is required'})
    
    # Set up the phone number (for now, we'll just store it in session)
    session['telegram_phone'] = phone_number
    telegram_bot.set_phone_number(phone_number)
    
    # For demo purposes, we'll assume the user will manually provide their chat_id
    # In a real implementation, you'd implement proper verification
    chat_id = data.get('chat_id')  # Optional for testing
    if chat_id:
        telegram_bot.set_chat_id(chat_id)
        session['telegram_enabled'] = True
        
        # Send welcome message
        telegram_bot.send_message(f"🎯 Welcome to Match The Pose! Your Telegram notifications are now enabled. Good luck with your poses! 💪")
    else:
        session['telegram_enabled'] = True  # Enable even without chat_id
        # Send welcome message (will be logged to console if no chat_id)
        telegram_bot.send_message(f"🎯 Welcome to Match The Pose! Your Telegram notifications are now enabled. Good luck with your poses! 💪")
    
    return jsonify({
        'success': True, 
        'message': 'Telegram setup completed!',
        'notifications_enabled': session.get('telegram_enabled', False)
    })

@app.route('/enable_telegram_notifications', methods=['POST'])
def enable_telegram_notifications():
    """Enable Telegram notifications with chat_id"""
    data = request.get_json()
    chat_id = data.get('chat_id', '').strip()
    
    if not chat_id:
        return jsonify({'success': False, 'error': 'Chat ID is required'})
    
    try:
        telegram_bot.set_chat_id(int(chat_id))
        session['telegram_enabled'] = True
        
        # Send test message
        telegram_bot.send_message("🎯 Telegram notifications enabled! You'll receive updates during your Match The Pose game. Good luck! 💪")
        
        return jsonify({'success': True, 'message': 'Telegram notifications enabled!'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid chat ID format'})

@app.route('/notify_pose_fail', methods=['POST'])
def notify_pose_fail():
    """Send Telegram notification when user fails a pose"""
    # Check if user has set up Telegram (even without chat_id)
    if not session.get('telegram_phone', None):
        return jsonify({'success': True, 'message': 'Telegram not set up'})
    
    data = request.get_json()
    pose_name = data.get('pose_name', '')
    pose_image = data.get('pose_image', '')
    
    print(f"🔍 DEBUG: Attempting to send pose failure notification for {pose_name}")
    
    if pose_name and pose_image:
        # Get the full path to the pose image
        pose_image_path = os.path.join(app.static_folder, pose_image)
        print(f"🔍 DEBUG: Image path: {pose_image_path}")
        
        # Send Telegram notification
        telegram_bot.send_pose_failure(pose_name, pose_image_path)
        
        return jsonify({'success': True, 'message': 'Telegram notification sent'})
    
    return jsonify({'success': False, 'error': 'Missing pose information'})

@app.route('/notify_game_end', methods=['POST'])
def notify_game_end():
    """Send final score via Telegram when game ends"""
    # Check if user has set up Telegram (even without chat_id)
    if not session.get('telegram_phone', None):
        return jsonify({'success': True, 'message': 'Telegram not set up'})
    
    data = request.get_json()
    final_score = data.get('final_score', session.get('score', 0))
    total_rounds = session.get('max_rounds', 10)
    
    print(f"🔍 DEBUG: Attempting to send final score notification. Score: {final_score}/{total_rounds * 5}")
    
    # Send final score notification
    telegram_bot.send_final_score(final_score, total_rounds)
    
    return jsonify({'success': True, 'message': 'Final score sent via Telegram'})

if __name__ == '__main__':
    app.run(debug=True)
