from fastapi import APIRouter, HTTPException
from app.services.mongo import MongoEngine  # Or wherever your MongoEngine is imported from

router = APIRouter()
mongo_engine = MongoEngine()

@router.get("/api/history")
async def get_prediction_history():
    """Retrieves the last 50 evaluation events from MongoDB Atlas."""
    try:
        history = await mongo_engine.get_recent_history(limit=50)
        # Force a fallback if history isn't a valid list
        return history if isinstance(history, list) else []
    except Exception as e:
        print(f"🔴 MONGODB ERROR DETECTED: {e}")
        # Returning an empty list instead of a 500 error prevents the React frontend from breaking!
        return []