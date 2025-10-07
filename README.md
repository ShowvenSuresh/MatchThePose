# Match The Pose

An interactive computer‑vision game that challenges players to replicate randomly selected poses using only their webcam. Real‑time landmark detection (MediaPipe) feeds a lightweight scikit‑learn classifier that identifies the player’s current pose, assigns a confidence score, and drives an adaptive scoring system. Optional Telegram integration delivers live notifications for missed poses and a personalized end‑of‑game summary.

---
## Highlights
- Real‑time pose recognition (MediaPipe + OpenCV)
- Gamified 10‑round session with anti‑repetition pose sequencing
- Confidence‑graded scoring (1–5 pts per successful round)
- Live visual feedback (bounding box color + confidence overlay)
- Optional Telegram notifications (missed pose + final score)
- Easily extensible pose library (drop images into /app/static/poses/<Pose Name>/)
- Compact logistic regression model for fast inference

---
## Gameplay Flow
1. Landing screen (page1.html) with music + optional Telegram setup
2. Countdown overlay → round begins (5‑second timer per pose)
3. Left panel: target pose image; Right panel: live webcam feed
4. System periodically (500 ms) checks current predicted pose & confidence
5. When timer hits 0:
   - If correct: points awarded based on confidence bracket
   - If incorrect: (optional) Telegram “pose failed” notification
6. Automatically loads next pose until 10 rounds complete
7. Final score displayed + (optional) Telegram summary sent

---
## Scoring System
Based on model confidence (percentage) at the moment the round ends AND only if the predicted pose matches the target:
- < 50%  → 1 point
- 50–59% → 2 points
- 60–69% → 3 points
- 70–79% → 4 points
- ≥ 80%  → 5 points
Maximum possible score: 10 rounds × 5 = 50 points.

---
## Technology Stack
Backend: Flask (session‑based round / score tracking)
Pose Detection: MediaPipe Pose (landmarks) + custom landmark filtering (body only, facial landmarks removed)
ML Model: Scikit‑learn logistic regression (loaded from app/model/logistic_regression_pose_classifier.pkl)
Computer Vision: OpenCV + custom drawing (dynamic box + overlay text)
Frontend: HTML templates + vanilla JS + responsive CSS
Notifications: Telegram Bot API (simple HTTP calls, no async complexity)

---
## Project Structure
```
MatchThePose/
├── app
│   ├── routes.py                 # Flask routes: game flow & API endpoints
│   ├── model/
│   │   └── logistic_regression_pose_classifier.pkl
│   ├── static/
│   │   ├── js/main.js
│   │   ├── music/                # Audio assets
│   │   ├── poses/                # Pose class folders (images per class)
│   │   └── styles/{styles.css,page2.css}
│   ├── templates/{page1.html,page2.html}
│   └── utils/
│       ├── camera.py             # Webcam + landmark extraction + overlay
│       ├── pose_matcher.py       # Feature extraction + model inference
│       └── telegram_bot.py       # Minimal Telegram wrapper
├── main.py                       # Entry point (runs Flask)
├── requirements.txt
└── README.md
```

---
## Installation
Prerequisites:
- Python 3.10+ (recommended)
- A functional webcam
- (Optional) Telegram account for notifications

1. Clone repository
```bash
git clone https://github.com/ShowvenSuresh/MatchThePose.git
cd MatchThePose
```
2. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. (Optional) Set up Telegram Bot
   - Talk to @BotFather → create bot → obtain token
   - In app/routes.py replace:
     TELEGRAM_TOKEN = "---"  # with your bot token
   - (Optional) Manually set chat ID by sending /start to your bot, then supplying it in the UI modal

5. Run the application
```bash
python main.py
```
6. Open in browser
```
http://localhost:5000
```

---
## Using Telegram Notifications
Types of notifications:
- Pose failure (includes a motivational message and the correct pose image)
- Final game summary (score + performance tier)

Enable Flow:
1. Click Start → Telegram modal appears
2. Enter a phone number (stored only in session) and optionally a chat ID
3. If chat ID not provided: messages are logged to console until set

Security Note: Do NOT commit real bot tokens or production secret keys.

---
## Adding / Updating Poses
1. Create a folder under: app/static/poses/<Pose Name>
2. Add one or more reference images (.jpg/.png)
3. The game auto-selects random images while enforcing:
   - No consecutive duplicate pose classes
   - Max usage per pose = 2 per 10‑round session
4. To train a new model (not included here):
   - Collect landmark sequences via MediaPipe
   - Build feature matrix (flattened (x,y,z,visibility) per landmark)
   - Train a classifier → export with joblib → replace existing .pkl
   - Update class_mapping in pose_matcher.py if label indices change

---
## Key Implementation Details
- Landmark Filtering: Face landmarks (indices 0–10) are excluded for clarity; only body topology is drawn.
- Prediction Loop: Video stream thread updates last_prediction + last_confidence; HTTP endpoints consume cached values to avoid contention.
- Expected Pose Coloring: Bounding box is green when predicted pose matches target, yellow otherwise.
- Session State: score, round index, pose sequence, and Telegram flags stored in Flask session.

---
## Potential Improvements (Roadmap Ideas)
- Calibration step for distance / scale normalization
- Difficulty modes (shorter timers / higher confidence thresholds)
- Leaderboard (persistent storage, e.g. SQLite or Redis)
- Async WebSocket streaming instead of MJPEG
- Model upgrade (e.g. temporal sequence model for smoother classification)
- Dockerfile + CI workflow

---
## Troubleshooting
Webcam not detected:
- Ensure another app is not locking the device
- On Linux, verify /dev/video0 permissions

Low confidence values:
- Improve lighting & ensure full body in frame
- Avoid fast motion during final countdown second

Telegram messages not arriving:
- Verify token & chat ID
- Send a manual /start message to the bot first

---
## Security & Configuration Notes
- Replace app.secret_key in routes.py for any real deployment
- Never hardcode production tokens; prefer environment variables (e.g. export TELEGRAM_TOKEN=...)
- Consider rate limiting or auth if exposing publicly

---
## License
MIT License (If a LICENSE file is not yet present, create one before distribution.)

---
## Acknowledgements
- MediaPipe by Google for fast landmark inference
- OpenCV community
- scikit‑learn ecosystem

Enjoy matching poses! 💪
