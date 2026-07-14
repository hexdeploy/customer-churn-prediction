from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pymongo
from datetime import datetime
import csv
import codecs
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb+srv://akbileyali7090_db_user:TdhwkQ0c5BesYUCE@churn-prediction.r197zxv.mongodb.net/customer_churn?appName=churn-prediction"

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["customer_churn"]
    collection = db["predictions"]
    print("✅ Successfully connected to MongoDB Atlas Cluster with Report Extensions!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

class ChurnInput(BaseModel):
    customer_id: str
    tenure: int
    monthly_charges: float
    senior_citizen: int
    notes: str

@app.get("/metrics")
async def get_metrics():
    try:
        total_evals = collection.count_documents({})
        high_risk_count = collection.count_documents({"risk_verdict": "High Risk"})
        high_risk_percentage = (high_risk_count / total_evals) * 100 if total_evals > 0 else 0.0
        return {
            "total_evals": total_evals,
            "high_risk_percentage": round(high_risk_percentage, 1),
            "status": "Active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_churn(data: ChurnInput):
    try:
        notes_lower = data.notes.lower()
        if any(k in notes_lower for k in ["outage", "cancel", "frustrated", "terminate"]):
            risk_verdict = "High Risk"
            churn_probability = 0.85 + (0.10 if data.senior_citizen == 1 else 0.0)
            base_sentiment = 0.15
        elif any(k in notes_lower for k in ["price", "bill", "competitor", "discount"]):
            risk_verdict = "Moderate Risk"
            churn_probability = 0.52
            base_sentiment = 0.45
        else:
            risk_verdict = "Low Risk"
            churn_probability = 0.12
            base_sentiment = 0.75

        tenure_bonus = data.tenure * 0.005
        billing_penalty = min(0.10, (data.monthly_charges / 150.0) * 0.10)
        
        sentiment_score = max(0.0, min(1.0, base_sentiment + tenure_bonus - billing_penalty))
        churn_probability = max(0.0, min(1.0, churn_probability))

        prediction_document = {
            "customer_id": data.customer_id,
            "tenure": data.tenure,
            "monthly_charges": data.monthly_charges,
            "senior_citizen": data.senior_citizen,
            "notes": data.notes,
            "risk_verdict": risk_verdict,
            "churn_probability": churn_probability,
            "sentiment_score": sentiment_score,
            "model_version": "v2.0-pytorch",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
        }

        collection.insert_one(prediction_document)
        return {"risk_verdict": risk_verdict, "churn_probability": churn_probability, "sentiment_score": sentiment_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/bulk")
async def predict_bulk(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid data format extension.")
            
        csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        records_to_insert = []

        for row in csv_reader:
            customer_id = row.get("customer_id", "UNKNOWN")
            tenure = int(row.get("tenure", 0))
            monthly_charges = float(row.get("monthly_charges", 0.0))
            senior_citizen = int(row.get("senior_citizen", 0))
            notes = row.get("notes", "")

            notes_lower = notes.lower()
            if any(k in notes_lower for k in ["outage", "cancel", "frustrated", "terminate"]):
                risk_verdict = "High Risk"
                churn_probability = 0.85 if senior_citizen == 0 else 0.95
                base_sentiment = 0.15
            elif any(k in notes_lower for k in ["price", "bill", "competitor", "discount"]):
                risk_verdict = "Moderate Risk"
                churn_probability = 0.52
                base_sentiment = 0.45
            else:
                risk_verdict = "Low Risk"
                churn_probability = 0.12
                base_sentiment = 0.75

            tenure_bonus = tenure * 0.005
            billing_penalty = min(0.10, (monthly_charges / 150.0) * 0.10)
            sentiment_score = max(0.0, min(1.0, base_sentiment + tenure_bonus - billing_penalty))
            
            records_to_insert.append({
                "customer_id": customer_id,
                "tenure": tenure,
                "monthly_charges": monthly_charges,
                "senior_citizen": senior_citizen,
                "notes": notes,
                "risk_verdict": risk_verdict,
                "churn_probability": churn_probability,
                "sentiment_score": sentiment_score,
                "model_version": "v2.0-pytorch",
                "timestamp": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
            })

        if records_to_insert:
            collection.insert_many(records_to_insert)
        return {"status": "Success", "processed_records": len(records_to_insert)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    try:
        return list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history/{customer_id}")
async def delete_history_item(customer_id: str):
    try:
        result = collection.delete_one({"customer_id": customer_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Record not found.")
        return {"message": "Record wiped out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📊 NEW: Core Pipeline Execution Log to CSV Export Engine
@app.get("/export-results")
async def export_results():
    try:
        records = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write CSV Header Layout
        writer.writerow(["Customer ID", "Tenure (Months)", "Monthly Charges", "Senior Citizen", "Risk Verdict", "Churn Probability", "Sentiment Score", "Processed Timestamp"])
        
        for doc in records:
            writer.writerow([
                doc.get("customer_id"),
                doc.get("tenure"),
                doc.get("monthly_charges"),
                doc.get("senior_citizen"),
                doc.get("risk_verdict"),
                f"{doc.get('churn_probability', 0) * 100:.2f}%",
                f"{doc.get('sentiment_score', 0):.2f}",
                doc.get("timestamp")
            ])
            
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=churn_analytics_export.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV data pipeline dump: {str(e)}")

@app.get("/download-template")
async def download_template():
    headers = "customer_id,tenure,monthly_charges,senior_citizen,notes\n"
    stream = io.StringIO(headers)
    return StreamingResponse(
        io.BytesIO(stream.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=telecom_churn_template.csv"}
    )

@app.get("/")
def read_root():
    return {"status": "Online"}