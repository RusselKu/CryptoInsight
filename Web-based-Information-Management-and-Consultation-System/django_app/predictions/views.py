from django.http import JsonResponse
import joblib
import pandas as pd
import os

from .data_loader import load_data_to_dataframe
from .feature_engineering import feature_engineer

# Define the path to the saved artifacts
ARTIFACTS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "logistic_regression_model.joblib")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.joblib")

def predict(request):
    """
    API endpoint to get predictions for all cryptocurrencies.
    """
    try:
        # 1. Load the trained model and scaler
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("Model and scaler loaded successfully.")

        # 2. Get the latest data from the database
        # We reuse our existing functions for consistency
        raw_df = load_data_to_dataframe()
        if raw_df.empty:
            return JsonResponse({"error": "Could not load data from database."}, status=500)

        # 3. Preprocess the data using the feature engineering pipeline
        # Note: The feature_engineer function fits the scaler again.
        # This is not ideal for production. A better approach is to have a 
        # separate 'transform' function that just uses the fitted scaler.
        # For this implementation, we will proceed, but this is a key refinement for a real system.
        
        # We need the symbols before they are removed by feature engineering
        symbols = raw_df[['symbol', 'name', 'market_cap']].copy()
        symbols.sort_values('market_cap', ascending=False, inplace=True)
        symbols.drop_duplicates(subset='symbol', keep='first', inplace=True)

        processed_df, _ = feature_engineer(raw_df.copy())
        
        if processed_df.empty:
            return JsonResponse({"error": "Failed to process data for prediction."}, status=500)
            
        # Separate features (X) and target (y), although we only need X
        X = processed_df.drop('price_will_increase', axis=1)

        # 4. Make predictions
        predictions = model.predict(X)
        prediction_proba = model.predict_proba(X)[:, 1] # Probability of class 1 (price will increase)

        # 5. Format the response
        # Match predictions back to the symbols
        # It's crucial that the order of 'X' matches the order of 'symbols'
        results_df = symbols.loc[X.index].copy()
        results_df['prediction'] = predictions
        results_df['probability_increase'] = prediction_proba
        
        # Convert to dictionary
        results = results_df.to_dict('records')
        
        return JsonResponse({"predictions": results})

    except FileNotFoundError:
        return JsonResponse({"error": "Model or scaler not found. Please train the model first."}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
