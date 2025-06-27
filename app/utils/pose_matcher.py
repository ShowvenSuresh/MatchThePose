import numpy as np
import joblib 
import pandas as pd
import warnings

class PoseMatcher:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        
        # Suppress the specific sklearn feature names warning
        warnings.filterwarnings("ignore", message="X does not have valid feature names")

    def extract_landmarks(self, pose_landmarks):
        """
        Convert pose landmarks to a flat list of (x, y, z, visibility) values
        """
        if not pose_landmarks:
            return None
        
        landmarks = []
        for lm in pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
        
        # Create feature names to match training data (simple numeric names)
        num_features = len(landmarks)
        feature_names = [str(i) for i in range(num_features)]
        
        # Convert to DataFrame with feature names
        features_array = np.array(landmarks).reshape(1, -1)
        features_df = pd.DataFrame(features_array, columns=feature_names)
        
        return features_df  

    def predict(self, pose_landmarks):
        features = self.extract_landmarks(pose_landmarks)
        if features is None:
            return "No pose detected"
        
        prediction = self.model.predict(features)
        return prediction[0]  # Return class label (e.g., "correct", "wrong")

    def predict_with_confidence(self, pose_landmarks):
        """
        Get prediction with confidence/similarity percentage
        """
        features = self.extract_landmarks(pose_landmarks)
        if features is None:
            return "No pose detected", 0.0
        
        prediction = self.model.predict(features)
        
        # Get prediction probabilities if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)
            confidence = np.max(probabilities) * 100  # Convert to percentage
        elif hasattr(self.model, 'decision_function'):
            # For SVM or similar models
            decision_scores = self.model.decision_function(features)
            # Normalize to 0-100 range (this is a simple approach)
            confidence = min(max((decision_scores[0] + 1) * 50, 0), 100)
        else:
            # Fallback: basic confidence based on feature consistency
            confidence = 75.0  # Default confidence when method not available
        
        return prediction[0], confidence
