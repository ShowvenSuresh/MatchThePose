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
            result = self.matcher.predict(results.pose_landmarks)
            self.last_prediction = result

            cv2.putText(frame, f"Pose: {result}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            self.last_prediction = "No pose detected"
            cv2.putText(frame, "No Pose Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Resize and encode
        frame = imutils.resize(frame, width=400)
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
