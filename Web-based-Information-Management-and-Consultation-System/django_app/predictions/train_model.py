import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# Import the data loading and feature engineering functions
from data_loader import load_data_to_dataframe
from feature_engineering import feature_engineer

# Define the path to save the model and scaler
ARTIFACTS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "logistic_regression_model.joblib")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.joblib")

def train_model():
    """
    Trains the logistic regression model and saves the artifacts.
    """
    # 1. Load Data
    raw_df = load_data_to_dataframe()
    if raw_df.empty:
        print("Data loading failed. Exiting training process.")
        return

    # 2. Feature Engineering
    processed_df, scaler = feature_engineer(raw_df)
    if processed_df.empty:
        print("Feature engineering failed. Exiting training process.")
        return

    # 3. Split Data
    X = processed_df.drop('price_will_increase', axis=1)
    y = processed_df['price_will_increase']
    
    # Using a random split for now. For a real-world scenario, a time-based split is recommended.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Data split into training and testing sets. Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    # 4. Train Model
    print("Training Logistic Regression model...")
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    print("Model training complete.")

    # 5. Evaluate Model
    print("\n--- Model Evaluation ---")
    y_pred = model.predict(X_test)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # 6. Save Artifacts
    print(f"Saving model to {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)
    
    print(f"Saving scaler to {SCALER_PATH}")
    joblib.dump(scaler, SCALER_PATH)

    print("\nModel and scaler saved successfully.")

if __name__ == "__main__":
    train_model()
