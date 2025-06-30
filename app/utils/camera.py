import cv2
import imutils
import mediapipe as mp
from app.utils.pose_matcher import PoseMatcher
# At the top of your file, add this import
from mediapipe.framework.formats import landmark_pb2

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        self.matcher = PoseMatcher("app/model/pose_classifier.pkl")
        self.last_prediction = "No pose detected"
        self.last_confidence = 0.0
        self.expected_pose = None  # Store the current expected pose

    def set_expected_pose(self, expected_pose):
        """
        Set the expected pose for comparison
        """
        self.expected_pose = expected_pose

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            raise RuntimeError("Could not read frame from camera")

        frame = cv2.flip(frame, 1)

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            # Step 1: Filter out face landmarks (indices 0 to 10)
            body_landmarks = landmark_pb2.NormalizedLandmarkList()
            for i in range(11, len(results.pose_landmarks.landmark)):
                body_landmarks.landmark.add().CopyFrom(results.pose_landmarks.landmark[i])

            # Step 2: Filter and remap connections
            new_connections = [
                (s - 11, e - 11) for (s, e) in self.mp_pose.POSE_CONNECTIONS
                if s >= 11 and e >= 11
            ]

            # Step 3: Draw only the body landmarks and connections
            self.mp_drawing.draw_landmarks(
                frame,
                body_landmarks,
                new_connections,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0),  # Green color for landmarks
                    thickness=2,
                    circle_radius=2
                ),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(255, 0, 0),  # Blue color for connections
                    thickness=2
                )
            )

            # Step 4: Use the original landmarks for pose matching
            result, confidence = self.matcher.predict_with_confidence(results.pose_landmarks)
            self.last_prediction = result
            self.last_confidence = confidence

            # Step 5: Draw detection box around the user
            self._draw_detection_box(frame, results.pose_landmarks, result, confidence)
        else:
            self.last_prediction = "No pose detected"
            self.last_confidence = 0.0
            # Draw a basic detection box even when no pose is detected
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (50, 50), (w-50, h-50), (0, 0, 255), 2)
            cv2.putText(frame, "No Pose Detected", (60, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Resize and encode
        frame = imutils.resize(frame, width=400)
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    
    def _draw_detection_box(self, frame, pose_landmarks, pose_result, confidence):
        """
        Draw a detection box around the user with pose information and similarity percentage
        """
        h, w = frame.shape[:2]
        
        # Calculate bounding box from pose landmarks
        x_coords = [lm.x * w for lm in pose_landmarks.landmark]
        y_coords = [lm.y * h for lm in pose_landmarks.landmark]
        
        # Add padding to the bounding box
        padding = 30
        x_min = max(0, int(min(x_coords)) - padding)
        x_max = min(w, int(max(x_coords)) + padding)
        y_min = max(0, int(min(y_coords)) - padding)
        y_max = min(h, int(max(y_coords)) + padding)
        
        # Determine box color based on pose matching
        if self.expected_pose and pose_result != "No pose detected":
            # Normalize pose names for comparison (same logic as in routes.py)
            predicted_normalized = pose_result.replace('_', ' ').replace('-', ' ').lower().strip()
            expected_normalized = self.expected_pose.replace('_', ' ').replace('-', ' ').lower().strip()
            
            if predicted_normalized == expected_normalized:
                box_color = (0, 255, 0)  # Green when poses match
            else:
                box_color = (0, 255, 255)  # Yellow when poses don't match
        else:
            box_color = (0, 255, 255)  # Yellow when no expected pose is set or no pose detected

        # Draw the detection box
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), box_color, 2)
        
        # Prepare text for display - combine pose and similarity on same line
        combined_text = f"Pose: {pose_result} | {confidence:.1f}%"
        
        # Draw background rectangles for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Get text size for background rectangle
        (text_w, text_h), _ = cv2.getTextSize(combined_text, font, font_scale, thickness)
        
        # Draw background rectangle at the top
        cv2.rectangle(frame, (x_min, y_min - text_h - 10), (x_min + text_w + 10, y_min), (0, 0, 0), -1)
        
        # Draw combined text at the top
        cv2.putText(frame, combined_text, (x_min + 5, y_min - 5), font, font_scale, box_color, thickness)
