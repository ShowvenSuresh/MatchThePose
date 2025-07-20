
# Match The Pose

**Match The Pose** is an interactive web application that uses your webcam to analyze your body poses in real-time. The game challenges you to match a series of randomly selected poses, providing instant feedback and scoring based on your accuracy. It also features Telegram integration to send you notifications about your progress.

## Features

- **Real-time Pose Matching:** Utilizes your webcam to detect and analyze your body poses.
- **Interactive Gameplay:** A fun and engaging game where you match a sequence of poses.
- **Scoring System:** Get scored based on how accurately you match the poses.
- **Telegram Integration:** Receive notifications on your Telegram about your game progress, including failed poses and final scores.
- **Variety of Poses:** Includes a diverse set of poses to keep the game challenging.

## Technologies Used

- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **Pose Detection:** MediaPipe
- **Machine Learning:** Scikit-learn
- **Image Processing:** OpenCV
- **Notifications:** Telegram Bot API

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/match-the-pose.git
   cd match-the-pose
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Telegram Bot:**
   - Create a new bot on Telegram by talking to the [BotFather](https://t.me/botfather).
   - Get your `TELEGRAM_TOKEN` and `CHAT_ID`.
   - Update the `TELEGRAM_TOKEN` in `app/routes.py`.

5. **Run the application:**
   ```bash
   python main.py
   ```

6. **Open your browser and go to `http://0.0.0.0:5000` to start the game.**

## How to Play

1. **Start the Game:** Click the "Start Game" button on the homepage.
2. **Allow Webcam Access:** Grant permission for the browser to access your webcam.
3. **Match the Pose:** A pose will be displayed on the screen. Try to match it with your body.
4. **Get Feedback:** The application will provide real-time feedback on your accuracy.
5. **Score Points:** Earn points for each correctly matched pose.
6. **Telegram Notifications:** If you've set up Telegram integration, you'll receive notifications about your progress.

## Project Structure

```
.
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── model
│   │   └── logistic_regression_pose_classifier.pkl
│   ├── static
│   │   └── poses
│   ├── templates
│   │   ├── page1.html
│   │   └── page2.html
│   └── utils
│       ├── __init__.py
│       ├── camera.py
│       ├── pose_matcher.py
│       └── telegram_bot.py
├── main.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
