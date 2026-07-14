import os
import sys
import torch
import numpy as np
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix

# Align paths to root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from training.train_pytorch import ChurnMLP
from training.dataset import get_validation_dataloader  # Adjust if your function name varies

def evaluate_network():
    print("📊 Evaluating PyTorch Neural Network Pipeline...")
    
    # Path mappings
    weights_path = os.path.join(PROJECT_ROOT, "app", "models", "churn_model.pt")
    features_path = os.path.join(PROJECT_ROOT, "app", "models", "model_features_order.pkl")
    
    if not os.path.exists(weights_path):
        print(f"❌ Error: Weights not found at {weights_path}. Train the model first.")
        return

    # Load parameters to determine architecture dimensions
    import joblib
    feature_columns = joblib.load(features_path)
    
    # Instantiate model structure
    model = ChurnMLP(input_dim=len(feature_columns))
    model.load_state_dict(torch.load(weights_path))
    model.eval()

    # Get validation dataset split (Assumes get_validation_dataloader handles this inside your dataset.py)
    try:
        val_loader = get_validation_dataloader()
    except AttributeError:
        # Fallback if your loader invocation structure inside dataset.py is different
        print("ℹ️ Custom data loader invocation skipped. Ensure dataset arrays are prepared.")
        return

    all_targets = []
    all_predictions = []

    with torch.no_grad():
        for inputs, targets in val_loader:
            outputs = model(inputs)
            all_targets.extend(targets.numpy())
            all_predictions.extend(outputs.numpy())

    all_targets = np.array(all_targets)
    all_predictions = np.array(all_predictions)
    binary_predictions = (all_predictions >= 0.5).astype(int)

    # Compute Core Target Metric: ROC-AUC (Goal: > 0.84)
    roc_auc = roc_auc_score(all_targets, all_predictions)
    
    print("\n--- Model Evaluation Summary ---")
    print(f"🎯 Target Baseline ROC-AUC: 0.84")
    print(f"🚀 PyTorch Model ROC-AUC:  {roc_auc:.4f}")
    print("---------------------------------")
    
    if roc_auc >= 0.84:
        print("✅ Success! Custom network beat or matched the baseline production metric.")
    else:
        print("ℹ️ Network running smoothly, optimize learning rates or epochs to push past baseline.")

    print("\n📋 Classification Report:")
    print(classification_report(all_targets, binary_predictions))

if __name__ == "__main__":
    evaluate_network()