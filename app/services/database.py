import redis
from pymongo import MongoClient

class StorageEngine:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", redis_host="localhost", redis_port=6379):
        """
        Manages high-throughput connections to persistent storage (MongoDB) 
        and the ultra-fast distributed caching layer (Redis).
        """
        print("🔄 Connecting to infrastructure backing engines...")
        
        # 1. Initialize MongoDB Client
        try:
            self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            # Reference a specific database and collection
            self.db = self.mongo_client["churn_analytics"]
            self.customer_collection = self.db["customer_profiles"]
            # Trigger a quick connection test
            self.mongo_client.server_info()
            print("💾 MongoDB Connected Successfully!")
        except Exception as e:
            print(f"⚠️ MongoDB Connection warning (Ensure instance is running): {e}")
            self.customer_collection = None

        # 2. Initialize Redis Caching Engine
        try:
            self.cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_timeout=2)
            self.cache.ping()
            print("⚡ Redis Caching Engine Connected Successfully!")
        except Exception as e:
            print(f"⚠️ Redis Connection warning (Ensure instance is running): {e}")
            self.cache = None

    def cache_prediction(self, customer_id: str, score: float, expiry_seconds=3600):
        """Stores a calculated prediction score in Redis with a Time-To-Live (TTL)."""
        if self.cache:
            try:
                self.cache.set(f"churn:{customer_id}", str(score), ex=expiry_seconds)
            except Exception as e:
                print(f"⚠️ Failed to write to Redis cache: {e}")

    def get_cached_prediction(self, customer_id: str):
        """Retrieves a cached prediction score from Redis if it exists."""
        if self.cache:
            try:
                cached_val = self.cache.get(f"churn:{customer_id}")
                return float(cached_val) if cached_val else None
            except Exception:
                return None
        return None

    def save_customer_record(self, record: dict):
        """Persists structural customer profiles and text logs into MongoDB."""
        if self.customer_collection is not None:
            try:
                self.customer_collection.update_one(
                    {"customerID": record.get("customerID")},
                    {"$set": record},
                    upsert=True
                )
            except Exception as e:
                print(f"⚠️ Failed to log record to MongoDB: {e}")