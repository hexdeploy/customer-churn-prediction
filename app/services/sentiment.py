import os
import sys
from transformers import pipeline

class SentimentScorer:
    def __init__(self):
        """
        Loads the pre-trained DistilBERT sentiment classification model.
        The model weights download automatically on the first execution.
        """
        print("🔄 Loading Hugging Face DistilBERT Pipeline...")
        self.analyzer = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        print("✅ DistilBERT Model Loaded Successfully!")
        
    def score_text(self, text: str) -> float:
        """
        Parses arbitrary text segments and yields a scaled distribution between 0.0 and 1.0.
        Highly negative notes drift toward 0.0, highly positive remarks hit near 1.0.
        """
        # Graceful handling for blank values or non-text features
        if not text or not str(text).strip():
            return 0.5  # Pure neutral fallback
            
        try:
            result = self.analyzer(str(text))[0]
            label = result['label']       # 'POSITIVE' or 'NEGATIVE'
            confidence = result['score']  # Real decimal probability float
            
            # Scale smoothly into continuous values
            if label == "POSITIVE":
                return float(confidence)
            else:
                return float(1.0 - confidence)
                
        except Exception as e:
            print(f"⚠️ NLP Processing Exception encountered: {e}. Falling back to 0.5")
            return 0.5