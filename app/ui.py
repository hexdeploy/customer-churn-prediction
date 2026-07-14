import os
import sys
import torch
import torch.nn as nn
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add project directories to paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from app.services.sentiment import SentimentScorer
from app.services.database import StorageEngine
from training.train_pytorch import ChurnMLP

app = FastAPI(title="Multimodal Churn Prediction Engine")

# --- GLOBAL INITIALIZATION ---
MODEL_DIR = os.path.join(CURRENT_DIR, "app", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pt")
SCALER_PATH = os.path.join(MODEL_DIR, "numerical_scaler.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "model_features_order.pkl")

# Lazy global loading instances
scaler = None
feature_columns = None
model = None
nlp_scorer = None
storage = None

@app.on_event("startup")
def startup_event():
    global scaler, feature_columns, model, nlp_scorer, storage
    
    # 1. Initialize services
    nlp_scorer = SentimentScorer()
    storage = StorageEngine()
    
    # 2. Load serialized ML states
    if os.path.exists(SCALER_PATH) and os.path.exists(FEATURES_PATH) and os.path.exists(MODEL_PATH):
        scaler = joblib.load(SCALER_PATH)
        feature_columns = joblib.load(FEATURES_PATH)
        
        # Instantiate network matching the input feature length
        model = ChurnMLP(input_dim=len(feature_columns))
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()
        print("🧠 PyTorch Model and Scalers fully active!")
    else:
        print("⚠️ Warning: Neural network model artifacts missing! Prediction endpoints will fail.")

# --- API BODY SCHEMA ---
class CustomerPayload(BaseModel):
    customerID: str = "0000-MOCK"
    SeniorCitizen: int = 0
    tenure: int = 12
    MonthlyCharges: float = 45.50
    TotalCharges: float = 546.00
    customer_notes: str = ""

@app.post("/predict")
async def predict_churn(payload: CustomerPayload):
    if model is None or scaler is None or feature_columns is None:
        raise HTTPException(status_code=500, detail="Prediction models not loaded.")
        
    data = payload.dict()
    customer_id = data["customerID"]
    
    # 1. Check Redis Cache
    cached_score = storage.get_cached_prediction(customer_id)
    if cached_score is not None:
        return {"customerID": customer_id, "churn_probability": cached_score, "source": "redis_cache"}
        
    # 2. Extract Multimodal NLP Sentiment Signal
    sentiment_signal = nlp_scorer.score_text(data["customer_notes"])
    
    # 3. Align features structurally to match layout 
    # Build a zero matrix with columns matching trained feature structure
    feature_vector = np.zeros(len(feature_columns), dtype=np.float32)
    
    # Direct tabular mappings
    direct_mappings = {
        'SeniorCitizen': data['SeniorCitizen'],
        'tenure': data['tenure'],
        'MonthlyCharges': data['MonthlyCharges'],
        'TotalCharges': data['TotalCharges'],
        'sentiment_score': sentiment_signal
    }
    
    for col, val in direct_mappings.items():
        if col in feature_columns:
            idx = feature_columns.index(col)
            feature_vector[idx] = val
            
    # Mock fallback assignments for missing encoded variables
    # (In real settings, map other user fields to match get_dummies keys)
    
    # 4. Transform features and pass to PyTorch inference engine
    feature_vector_scaled = scaler.transform([feature_vector])
    
    with torch.no_grad():
        input_tensor = torch.tensor(feature_vector_scaled, dtype=torch.float32)
        prediction_prob = model(input_tensor).item()
        
    # 5. Persist background transaction states asynchronously
    storage.cache_prediction(customer_id, prediction_prob)
    data["computed_sentiment"] = sentiment_signal
    data["churn_risk_score"] = prediction_prob
    storage.save_customer_record(data)
    
    return {
        "customerID": customer_id,
        "churn_probability": round(prediction_prob, 4),
        "sentiment_score_injected": round(sentiment_signal, 4),
        "source": "pytorch_inference"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "components": {"neural_network": model is not None}}