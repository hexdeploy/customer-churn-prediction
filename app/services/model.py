import os
import sys
import torch
import joblib
import numpy as np

# Dynamically find paths relative to this file's location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # Walks up to 'app/'
MODELS_DIR = os.path.join(ROOT_DIR, "models")

# Ensure training directory is in path so Python can find ChurnMLP definition
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from training.train_pytorch import ChurnMLP

class ChurnModelEngine:
    def __init__(self):
        """
        Loads the trained PyTorch MLP architecture weights and pre-fitted 
        numerical scalers from the app/models/ directory.
        """
        print("🧠 Initializing PyTorch Inference Engine...")
        
        # Absolute asset path mapping
        self.scaler_path = os.path.join(MODELS_DIR, "numerical_scaler.pkl")
        self.features_path = os.path.join(MODELS_DIR, "model_features_order.pkl")
        self.weights_path = os.path.join(MODELS_DIR, "churn_model.pt")
        
        # Load pre-processing artifacts safely
        if not os.path.exists(self.weights_path):
            raise FileNotFoundError(f"Missing model weights at {self.weights_path}! Run training/train_pytorch.py first.")
            
        self.scaler = joblib.load(self.scaler_path)
        self.feature_columns = joblib.load(self.features_path)
        
        # Reconstruct network architecture using the feature dimensions count (20 inputs)[cite: 1]
        self.model = ChurnMLP(input_dim=len(self.feature_columns))
        self.model.load_state_dict(torch.load(self.weights_path))
        self.model.eval()  # Put network into evaluation mode (disables dropout)[cite: 1]
        print("✅ PyTorch Neural Network Weights Loaded and Ready!")

    def predict(self, input_data: dict, sentiment_score: float) -> float:
        """
        Accepts a dictionary of incoming customer features, injects the Hugging Face 
        sentiment score, aligns structural column layout, and runs PyTorch inference[cite: 1].
        """
        # Create an empty input array matching our required features length
        feature_vector = np.zeros(len(self.feature_columns), dtype=np.float32)
        
        # Map raw fields directly 
        direct_mappings = {
            'SeniorCitizen': input_data.get('SeniorCitizen', 0),
            'tenure': input_data.get('tenure', 0),
            'MonthlyCharges': input_data.get('MonthlyCharges', 0.0),
            'TotalCharges': input_data.get('TotalCharges', 0.0),
            'sentiment_score': sentiment_score  # Injected NLP feature[cite: 1]
        }
        
        # Dynamic alignment to match training columns positional order
        for col, val in direct_mappings.items():
            if col in self.feature_columns:
                idx = self.feature_columns.index(col)
                feature_vector[idx] = val
                
        # Scale numerical spaces using our training scaling parameters
        scaled_vector = self.scaler.transform([feature_vector])
        
        # Convert array to tensor and compute forward pass inference
        with torch.no_grad():
            tensor_input = torch.tensor(scaled_vector, dtype=torch.float32)
            probability = self.model(tensor_input).item()
            
        return float(probability)