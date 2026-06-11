import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Customer Churn Prediction API",
    description="Production API endpoint to assess customer churn probability thresholds.",
    version="1.0.0"
)

# 2. Define the Incoming Data Schema using Pydantic
class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

# 3. Load Pipeline Artifacts safely on Startup
try:
    model = joblib.load("best_churn_model.pkl")
    model_features_order = joblib.load("model_features_order.pkl")
    numerical_cols = joblib.load("numerical_cols_list.pkl")
    scaler = joblib.load("numerical_scaler.pkl")
except Exception as e:
    raise RuntimeError(f"Failed to load core model artifact dependencies locally: {e}")

# 4. Core Prediction Endpoint
@app.post("/predict")
async def predict_churn(data: CustomerData):
    try:
        # Convert incoming JSON schema smoothly into a Pandas DataFrame
        input_dict = data.model_dump()
        df_input = pd.DataFrame([input_dict])
        
        # Scale the numerical metrics precisely using the saved training scaler
        df_input[numerical_cols] = scaler.transform(df_input[numerical_cols])
        
        # Apply One-Hot Encoding to match categorical pipeline dimensions
        df_encoded = pd.get_dummies(df_input)
        
        # Reindex variables dynamically to align with training structural arrays
        df_final = df_encoded.reindex(columns=model_features_order, fill_value=0)
        
        # --- THE FIX: Extract Class 1 (Churn) Probability directly ---
        all_probabilities = model.predict_proba(df_final)[0]
        churn_probability = float(all_probabilities[1]) * 100
        
        # Map output flag cleanly based on the math probability threshold
        churn_prediction = 1 if churn_probability >= 50.0 else 0
        
        return {
            "churn_prediction": churn_prediction,
            "churn_probability_percentage": round(churn_probability, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Engine Error: {str(e)}")

# Health checkpoint check
@app.get("/")
async def root():
    return {"status": "healthy", "service": "Customer Churn API"}