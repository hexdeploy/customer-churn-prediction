import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data(filepath):
    print("--- Step 1: Loading and Preprocessing Data ---")
    df = pd.read_csv(filepath)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    
    # 1. Drop identifier column immediately to prevent scaler/encoder errors
    if 'customerID' in df.columns:
        df = df.drop(columns=['customerID'])
        print("Dropped 'customerID' column.")
        
    # 2. Clean 'TotalCharges' (converts spaces to NaN, then fills with median)
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].replace(' ', np.nan), errors='coerce')
        df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())
    
    # 3. Separate Features and Target
    if 'Churn' in df.columns:
        X = df.drop(columns=['Churn'])
        y = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() in ['yes', '1', 'true'] else 0)
    else:
        raise ValueError("Target column 'Churn' not found in the dataset.")
        
    # 4. Use One-Hot Encoding for categorical features (Robust for APIs)
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    print(f"Numerical features to scale: {numerical_cols}")
    print(f"Categorical features to One-Hot Encode: {categorical_cols}")
    
    # Convert text columns to binary 0/1 columns
    X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # Standardize column naming types to boolean/int for consistency
    X_encoded = X_encoded.astype({col: int for col in X_encoded.select_dtypes(include=['bool']).columns})
        
    return X_encoded, y, numerical_cols

def train_and_save_pipeline(filepath):
    # Process data
    X, y, numerical_cols = load_and_preprocess_data(filepath)
    
    # Capture the exact column names and structure the model expects
    model_features = X.columns.tolist()
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\n--- Step 2: Scaling Numerical Features ---")
    scaler = StandardScaler()
    X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
    X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])
    
    print("\n--- Step 3: Training Balanced Models ---")
    lr_model = LogisticRegression(class_weight='balanced', random_state=42)
    rf_model = RandomForestClassifier(class_weight='balanced', random_state=42)
    
    # Train and evaluate models
    lr_model.fit(X_train, y_train)
    lr_probs = lr_model.predict_proba(X_test)[:, 1]
    
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    
    rf_auc = roc_auc_score(y_test, rf_probs)
    lr_auc = roc_auc_score(y_test, lr_probs)
    
    print("\n" + "═"*45)
    print("MODEL PERFORMANCE SUMMARY (Balanced)")
    print("═"*45)
    print(f"Logistic Regression -> Accuracy: {accuracy_score(y_test, lr_model.predict(X_test))*100:.2f}% | AUC: {lr_auc:.4f}")
    print(f"Random Forest       -> Accuracy: {accuracy_score(y_test, rf_preds)*100:.2f}% | AUC: {rf_auc:.4f}")
    print("═"*45)
    
    # Select best model based on AUC performance
    if rf_auc > lr_auc:
        best_model = rf_model
        print("Selected Best Model: Random Forest")
    else:
        best_model = lr_model
        print("Selected Best Model: Logistic Regression")
        
    print("\n--- Step 4: Exporting Level 1 Artifacts ---")
    # We clean up the files! No more massive list of label encoders.
    joblib.dump(best_model, 'best_churn_model.pkl')
    joblib.dump(scaler, 'numerical_scaler.pkl')
    joblib.dump(numerical_cols, 'numerical_cols_list.pkl')
    joblib.dump(model_features, 'model_features_order.pkl')
    
    print("Successfully exported: best_churn_model.pkl, numerical_scaler.pkl, numerical_cols_list.pkl, model_features_order.pkl")
    print("Pipeline optimization complete!")

if __name__ == "__main__":
    # Replace this path with your local Telco Churn CSV file path
    DATASET_PATH = r"C:\Users\ANUP\OneDrive\Desktop\Projects\customer churn prediction project\WA_Fn-UseC_-Telco-Customer-Churn.csv" 
    train_and_save_pipeline(DATASET_PATH)