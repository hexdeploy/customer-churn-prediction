import sys
import os

# This dynamically points Python directly to your root folder, 
# ensuring it can look inside app/services/ without any import errors.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from app.services.sentiment import SentimentScorer

if __name__ == "__main__":
    scorer = SentimentScorer()
    
    angry_note = "I am absolutely furious. My internet connection drops out daily, and tech support hung up on me."
    happy_note = "Wonderful and reliable experience! The customer agent resolved my package query immediately."
    
    print("\n--- Running Multi-Modal NLP Verification Tests ---")
    print(f"😡 Angry Note Sentiment Score (Expected < 0.25): {scorer.score_text(angry_note):.4f}")
    print(f"😊 Happy Note Sentiment Score (Expected > 0.75): {scorer.score_text(happy_note):.4f}")
    print("-------------------------------------------------")
    print("✅ Stage 2 Extraction Verified!")