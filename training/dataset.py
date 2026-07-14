import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class ChurnDataset(Dataset):
    def __init__(self, X, y):
        """
        Custom PyTorch Dataset for tabular churn data + placeholder for sentiment signal.
        Converts data arrays directly into torch tensors for training.
        """
        # Convert inputs to float32 tensors, targets to float32 tensors with a singleton dimension
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def prepare_data(csv_path, target_column='Churn', test_size=0.2, random_state=42):
    """
    Reads the dataset, performs data cleaning, mock text-signal parsing, 
    and handles tensor splitting for model optimization.
    """
    df = pd.read_csv(csv_path)
    
    # Simple data cleanup for missing values (like total charges spaces)
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].astype(str).str.strip(), errors='coerce')
        df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())
        
    # Drop unique non-predictive identifier columns if they exist
    df = df.drop(columns=[col for col in ['customerID', 'customer_id'] if col in df.columns], errors='ignore')
    
    # Simulated engineering step: Injecting a temporary neutral sentiment score (0.5) 
    # to serve as a feature column until our Hugging Face module is fully active
    if 'sentiment_score' not in df.columns:
        df['sentiment_score'] = 0.5
        
    # Isolate targets
    if target_column in df.columns:
        # Map string targets to numeric if needed (e.g., 'Yes'/'No' to 1/0)
        if df[target_column].dtype == 'object':
            df[target_column] = df[target_column].map({'Yes': 1, 'No': 0, '1': 1, '0': 0})
        y = df[target_column].fillna(0).values
        X_raw = df.drop(columns=[target_column])
    else:
        raise ValueError(f"Target column '{target_column}' not found in the dataset.")
        
    # Convert all categorical text columns to numeric codes via One-Hot Encoding
    X_encoded = pd.get_dummies(X_raw, drop_first=True)
    
    # Align structural datatypes to floating parameters
    X_encoded = X_encoded.astype(np.float32)
    
    # Split the records into balanced training and evaluation subsets
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded.values, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Scale continuous distributions smoothly
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, X_test, y_train, y_test, scaler, X_encoded.columns.tolist()