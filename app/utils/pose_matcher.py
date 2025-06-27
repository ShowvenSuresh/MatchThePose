import numpy as np
import joblib 

class PoseMatcher:
    def __init__(self, model_path):
        self.model = joblib.load(model_path) 

    def extract_landmarks(self, pose_landmarks):
        """
        Convert pose landmarks to a flat list of (x, y, z, visibility) values
        """
        if not pose_landmarks:
            return None
        
        landmarks = []
        for lm in pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
        
        return np.array(landmarks).reshape(1, -1)  

    def predict(self, pose_landmarks):
        features = self.extract_landmarks(pose_landmarks)
        if features is None:
            return "No pose detected"
        
        prediction = self.model.predict(features)
        return prediction[0]  # Return class label (e.g., "correct", "wrong")
