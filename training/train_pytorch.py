import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import joblib
from sklearn.metrics import roc_auc_score, accuracy_score

# --- AUTOMATIC PATH FIXES ---
# Find the exact folder where this file (train_pytorch.py) lives
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Add it to Python's search path so it finds dataset.py perfectly
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# Look one folder up to find the root directory where telecom_churn.csv sits
ROOT_DIR = os.path.dirname(CURRENT_DIR)
CSV_PATH = os.path.join(ROOT_DIR, "telecom_churn.csv")
MODEL_DIR = os.path.join(ROOT_DIR, "app", "models")

# Now import your custom dataset functions safely
from dataset import prepare_data, ChurnDataset

# 1. Define the Neural Network Architecture
class ChurnMLP(nn.Module):
    def __init__(self, input_dim):
        super(ChurnMLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2), 
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid() 
        )
        
    def forward(self, x):
        return self.network(x)

# 2. Main Training Loop
def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print(f"🔄 Looking for data at: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Missing dataset! Please run generate_mock_data.py first.")
        
    print("🔄 Processing dataset and aligning feature dimensions...")
    X_train, X_test, y_train, y_test, scaler, feature_columns = prepare_data(CSV_PATH)
    
    # Instantiate custom PyTorch datasets and loaders
    train_dataset = ChurnDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    
    # Initialize the architecture
    input_dim = X_train.shape[1]
    model = ChurnMLP(input_dim)
    
    criterion = nn.BCELoss() 
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    
    epochs = 20
    print(f"🚀 Starting training for {epochs} Epochs...")
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * X_batch.size(0)
            
        total_epoch_loss = epoch_loss / len(train_loader.dataset)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1}/{epochs} | Loss: {total_epoch_loss:.4f}")
            
    # 3. Model Evaluation Verification
    model.eval()
    with torch.no_grad():
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
        predictions = model(X_test_tensor).numpy()
        
    y_pred_binary = (predictions >= 0.5).astype(int)
    auc_score = roc_auc_score(y_test, predictions)
    acc_score = accuracy_score(y_test, y_pred_binary)
    
    print("\n📊 Model Benchmark Verification Metrics:")
    print(f"   Peak ROC-AUC Score : {auc_score:.4f}")
    print(f"   Overall Accuracy   : {acc_score * 100:.2f}%")
    
    # 4. Serialize Matrix Artifacts
    print(f"\n📦 Saving artifacts to: {MODEL_DIR}...")
    torch.save(model.state_dict(), os.path.join(MODEL_DIR, "churn_model.pt"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "numerical_scaler.pkl"))
    joblib.dump(feature_columns, os.path.join(MODEL_DIR, "model_features_order.pkl"))
    print("✅ Step 1 Optimization complete!")

if __name__ == "__main__":
    train_model()