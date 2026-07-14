import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from app.services.database import StorageEngine

if __name__ == "__main__":
    print("--- Running Backend Storage Infrastructure Checks ---")
    engine = StorageEngine()
    
    # Run mock transactional check
    mock_id = "1234-TEST"
    print("\nTesting local caching writes...")
    engine.cache_prediction(mock_id, 0.8451, expiry_seconds=10)
    cached_score = engine.get_cached_prediction(mock_id)
    
    if cached_score:
        print(f"✅ Redis Pipeline Working! Retrieved cached score: {cached_score}")
    else:
        print("ℹ️ Redis not actively running or reachable locally, skipping volatile cache step.")
        
    print("-----------------------------------------------------")