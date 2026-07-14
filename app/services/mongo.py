import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Read from environmental variables or default to a safe local connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

class MongoEngine:
    def __init__(self):
        print("🔄 Initializing Async Motor client...")
        self.client = AsyncIOMotorClient("mongodb+srv://akbileyali7090_db_user:TdhwkQ0c5BesYUCE@churn-prediction.r197zxv.mongodb.net/customer_churn?appName=churn-prediction")
        # Match database schema layout from Blueprint 
        self.db = self.client["churn_analytics"]
        self.history_collection = self.db["prediction_history"]

    async def save_prediction_record(self, customer_id: str, input_features: dict, churn_probability: float, model_version: str = "v2.0-pytorch"):
        """Logs prediction payload securely to MongoDB Atlas asynchronously."""
        document = {
            "customer_id": customer_id,
            "input_features": input_features,
            "churn_probability": churn_probability,
            "timestamp": datetime.utcnow(),
            "model_version": model_version
        }
        try:
            await self.history_collection.insert_one(document)
        except Exception as e:
            print(f"⚠️ Async MongoDB logging failed: {e}")

    async def get_recent_history(self, limit: int = 50):
        """Returns the last N predictions from MongoDB for the history table endpoint."""
        cursor = self.history_collection.find().sort("timestamp", -1).limit(limit)
        history = []
        async for document in cursor:
            # Clean up object ID string representation for clean API response serialization
            document["_id"] = str(document["_id"])
            history.append(document)
        return history