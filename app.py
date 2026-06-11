from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn

# Initialize the FastAPI Application
app = FastAPI(title="Customer Churn Prediction API", version="1.0")

# --- Step 1: Load your saved ML Artifacts when the server boots up ---
try:
    model = joblib.load('best_churn_model.pkl')
    scaler = joblib.load('numerical_scaler.pkl')
    numerical_cols = joblib.load('numerical_cols_list.pkl')
    model_features = joblib.load('model_features_order.pkl')
    print("🎉 All ML artifacts loaded successfully! API is ready.")
except Exception as e:
    print(f"❌ Error loading model artifacts: {e}")
    raise RuntimeError("Could not find or load serialization (.pkl) files.")

# --- Step 2: Define the input structure (Data Validation) ---
# This ensures that any incoming request matches the features of your original dataset.
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

@app.get("/")
def home():
    return {"message": "Customer Churn Prediction API is active. Go to /docs to test it!"}

@app.post("/predict")
def predict_churn(customer: CustomerData):
    try:
        # 1. Convert incoming JSON request payload into a Pandas DataFrame
        input_dict = customer.dict()
        df_input = pd.DataFrame([input_dict])
        
        # 2. Re-apply One-Hot Encoding just like we did in the training script
        categorical_cols = df_input.select_dtypes(include=['object']).columns.tolist()
        df_encoded = pd.get_dummies(df_input, columns=categorical_cols)
        
        # 3. Structural Alignment (Crucial for API stability)
        # Force the input data to have the exact columns in the exact order as training.
        # If a category is missing for this single customer, it sets that column to 0.
        for col in model_features:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
                
        # Reorder columns to match the trained model's expectations perfectly
        df_encoded = df_encoded[model_features]
        
        # 4. Scale the numerical columns using our saved scaler parameters
        df_encoded[numerical_cols] = scaler.transform(df_encoded[numerical_cols])
        
        # 5. Generate Inference / Predictions
        prediction = model.predict(df_encoded)[0]
        probability = model.predict_proba(df_encoded)[0][1]
        
        # 6. Return response payload
        return {
            "churn_prediction": "Yes" if prediction == 1 else "No",
            "churn_probability_percentage": round(float(probability) * 100, 2),
            "status": "Success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Engine Error: {str(e)}")

if __name__ == "__main__":
    # Launch the local Uvicorn web server
    uvicorn.run(app, host="127.0.0.1", port=8000)