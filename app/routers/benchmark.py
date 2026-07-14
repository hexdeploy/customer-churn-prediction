from fastapi import APIRouter
from app.services.mongo import MongoEngine
import numpy as np

router = APIRouter()
mongo_engine = MongoEngine()

@router.get("/api/benchmark")
async def get_summary_metrics():
    """Aggregates collection stats for the frontend dashboard metrics panel[cite: 1]."""
    try:
        # Fetch records to calculate active run stats
        records = await mongo_engine.get_recent_history(limit=500)
        
        if not records:
            return {
                "total_predictions": 0,
                "avg_churn_probability": 0.0,
                "high_risk_count": 0
            }
            
        probabilities = [r["churn_probability"] for r in records]
        high_risk = sum(1 for p in probabilities if p >= 0.5)
        
        return {
            "total_predictions": len(records),
            "avg_churn_probability": round(float(np.mean(probabilities)), 4),
            "high_risk_count": high_risk
        }
    except Exception:
        return {
            "total_predictions": 0,
            "avg_churn_probability": 0.0,
            "high_risk_count": 0
        }