import asyncio
import telegram
import os
import threading
import requests
import random
from telegram.error import TelegramError

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.chat_id = None
        self.phone_number = None
        
    def set_phone_number(self, phone_number):
        """Set the phone number for the user"""
        self.phone_number = phone_number
        # For demo purposes, we'll use a simple mapping
        # In a real app, you'd need to implement proper user verification
        self.chat_id = self._get_chat_id_from_phone(phone_number)
        
    def _get_chat_id_from_phone(self, phone_number):
        """this no use, cannot delete"""

    def set_chat_id(self, chat_id):
        """Manually set chat_id (for testing purposes)"""
        self.chat_id = chat_id
    
    def send_message_simple(self, message):
        """Send a message using simple HTTP requests instead of async"""
        if not self.chat_id:
            print(f"No chat_id set. Message would be: {message}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Telegram message sent successfully")
                return True
            else:
                print(f"❌ Failed to send message. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_photo_simple(self, photo_path, caption=""):
        """Send a photo using simple HTTP requests instead of async"""
        if not self.chat_id:
            print(f"No chat_id set. Photo would be sent: {photo_path} with caption: {caption}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                
            if response.status_code == 200:
                print(f"✅ Telegram photo sent successfully")
                return True
            else:
                print(f"❌ Failed to send photo. Status: {response.status_code}, Response: {response.text}")
                return False
        except FileNotFoundError:
            print(f"❌ Photo file not found: {photo_path}")
            return False
        except Exception as e:
            print(f"❌ Error sending photo: {e}")
            return False
    
    def send_message(self, message):
        """Send a message synchronously using simple HTTP"""
        return self.send_message_simple(message)
    
    def send_photo(self, photo_path, caption=""):
        """Send a photo synchronously using simple HTTP"""
        return self.send_photo_simple(photo_path, caption)
    
    def send_pose_failure(self, pose_name, pose_image_path):
        """Send notification when user fails a pose"""
        print(f"🔍 DEBUG: send_pose_failure called for {pose_name}")
        
        # Multiple failure message variations for variety
        failure_messages = [
            f"❌ Oops! You failed to match the '{pose_name}' pose. Keep trying! 💪",
            f"🤔 Not quite right with the '{pose_name}' pose. Give it another shot! 🎯",
            f"😅 Almost there! The '{pose_name}' pose needs a bit more practice. You got this! 💯",
            f"🔄 Try again! The '{pose_name}' pose is tricky but you can nail it! 🌟",
            f"⚡ So close! Let's perfect that '{pose_name}' pose together! 🔥",
            f"🎪 Don't worry! Even yoga masters had to practice the '{pose_name}' pose. Keep going! 🧘‍♀️",
            f"🌈 Practice makes perfect! The '{pose_name}' pose will be yours soon! ✨",
            f"🎮 Game on! Ready for another attempt at the '{pose_name}' pose? 🕹️",
            f"🏃‍♂️ Keep moving! The '{pose_name}' pose is waiting for you to conquer it! 🏆",
            f"💫 Stay focused! You're getting closer to mastering the '{pose_name}' pose! 🎯"
        ]
        
        # Randomly select a failure message
        message = random.choice(failure_messages)
        
        # Send message first
        print(f"🔍 DEBUG: Sending failure message: {message}")
        self.send_message(message)
        
        # Then send the pose image
        if os.path.exists(pose_image_path):
            caption = f"Here's the '{pose_name}' pose you need to match:"
            print(f"🔍 DEBUG: Sending pose image: {pose_image_path}")
            self.send_photo(pose_image_path, caption)
        else:
            print(f"🔍 DEBUG: Image file not found: {pose_image_path}")
    
    def send_final_score(self, score, total_rounds):
        """Send final score notification"""
        print(f"🔍 DEBUG: send_final_score called with score {score}/{total_rounds * 5}")
        percentage = (score / (total_rounds * 5)) * 100  # Max 5 points per round
        
        # Different message variations based on performance
        if percentage >= 80:
            emoji = "🏆"
            message_variations = [
                "Amazing! You're a pose master!",
                "Incredible performance! You nailed it!",
                "Outstanding! You're a natural!",
                "Phenomenal! Pure pose perfection!",
                "Spectacular! You've mastered the art!"
            ]
        elif percentage >= 60:
            emoji = "🥈"
            message_variations = [
                "Great job! You're getting really good!",
                "Excellent work! Keep up the momentum!",
                "Well done! You're improving fast!",
                "Impressive! You're on the right track!",
                "Fantastic effort! You're almost there!"
            ]
        elif percentage >= 40:
            emoji = "🥉"
            message_variations = [
                "Good effort! Practice makes perfect!",
                "Nice try! You're making progress!",
                "Solid attempt! Keep pushing forward!",
                "Decent work! You're getting the hang of it!",
                "Fair play! Every step counts!"
            ]
        else:
            emoji = "💪"
            message_variations = [
                "Keep practicing! You'll get there!",
                "Don't give up! Every master was once a beginner!",
                "Stay strong! Progress takes time!",
                "Keep going! You're learning with each try!",
                "Never quit! The journey is just beginning!"
            ]
        
        message_type = random.choice(message_variations)
        
        # Additional closing variations
        closing_messages = [
            "Thanks for playing Match The Pose! 🎯",
            "Hope you had fun with Match The Pose! 🎮",
            "Great session of Match The Pose! 🌟",
            "Another round of Match The Pose complete! ⭐",
            "Match The Pose adventure finished! 🎊"
        ]
        
        closing = random.choice(closing_messages)
        
        message = f"""
{emoji} Game Complete! {emoji}

Final Score: {score}/{total_rounds * 5} points
Accuracy: {percentage:.1f}%

{message_type} {closing}
        """.strip()
        
        print(f"🔍 DEBUG: Sending final score message: {message}")
        self.send_message(message)
