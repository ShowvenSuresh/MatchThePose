import numpy as np
import joblib 
import pandas as pd
import warnings

class PoseMatcher:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        
        # Suppress the specific sklearn feature names warning
        warnings.filterwarnings("ignore", message="X does not have valid feature names")
        
        # Class label mapping (adjust based on your model's training)
        # This maps numeric predictions to pose names
        self.class_mapping = {
            0: "Ardha Chandrasana",
            1: "Arjaneyasana", 
            2: "Biceps Curl",
            3: "Dragon Kung Fu",
            4: "Front Double Biceps",
            5: "Front Lat Spread",
            6: "Hand-to-Big-Toe",
            7: "IP Man Squat",
            8: "Lat Pulldown",
            9: "Son of Zeus",
            10: "The Flash",
            11: "Utthita Parsvakonasana"
        }

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
        # Convert numeric prediction to pose name
        numeric_prediction = prediction[0]
        if isinstance(numeric_prediction, (int, np.integer)):
            return self.class_mapping.get(numeric_prediction, f"Unknown pose ({numeric_prediction})")
        else:
            return str(numeric_prediction)  # In case it's already a string

    def predict_with_confidence(self, pose_landmarks):
        """
        Get prediction with confidence/similarity percentage
        """
        features = self.extract_landmarks(pose_landmarks)
        if features is None:
            return "No pose detected", 0.0
        
        prediction = self.model.predict(features)
        
        # Convert numeric prediction to pose name
        numeric_prediction = prediction[0]
        if isinstance(numeric_prediction, (int, np.integer)):
            pose_name = self.class_mapping.get(numeric_prediction, f"Unknown pose ({numeric_prediction})")
        else:
            pose_name = str(numeric_prediction)  # In case it's already a string
        
        # Get prediction probabilities if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)
            confidence = np.max(probabilities) * 100  # Convert to percentage
        elif hasattr(self.model, 'decision_function'):
            # For SVM or similar models
            decision_scores = self.model.decision_function(features)
            
            # Handle different shapes of decision_scores
            if decision_scores.ndim == 1:
                # Binary classification or single sample
                max_score = np.max(np.abs(decision_scores))
            else:
                # Multi-class classification - get the max score
                max_score = np.max(decision_scores)
            
            # Normalize to 0-100 range
            # For SVM, decision scores can vary widely, so we use a sigmoid-like function
            confidence = min(max((max_score / (1 + np.abs(max_score))) * 100, 0), 100)
        else:
            # Fallback: basic confidence based on feature consistency
            confidence = 75.0  # Default confidence when method not available
        
        return pose_name, confidence
