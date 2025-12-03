from django.http import JsonResponse
import joblib
import pandas as pd
import os

from .data_loader import load_data_to_dataframe
from .feature_engineering import feature_engineer
from .data_loader_binance import load_binance_data_to_dataframe
from .feature_engineering_binance import feature_engineer_binance
from .data_loader_wazirx import load_wazirx_data_to_dataframe
from .feature_engineering_wazirx import feature_engineer_wazirx
from utils.mongo_conn import get_historical_binance_data, get_historical_wazirx_data


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

# Define the path to the saved artifacts for Binance
BINANCE_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "logistic_regression_model_binance.joblib")
BINANCE_SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler_binance.joblib")

def predict_binance(request):
    """
    API endpoint to get predictions for Binance cryptocurrencies.
    """
    try:
        model_binance = joblib.load(BINANCE_MODEL_PATH)
        scaler_binance = joblib.load(BINANCE_SCALER_PATH)
        print("Binance model and scaler loaded successfully.")

        raw_df_binance = load_binance_data_to_dataframe()
        if raw_df_binance.empty:
            return JsonResponse({"error": "Could not load Binance data from database."}, status=500)
        
        # We need the symbols before they are removed by feature engineering
        symbols_binance = raw_df_binance[['symbol']].copy()

        processed_df_binance, _ = feature_engineer_binance(raw_df_binance.copy())
        
        if processed_df_binance.empty:
            return JsonResponse({"error": "Failed to process Binance data for prediction."}, status=500)
            
        X_binance = processed_df_binance.drop('price_will_increase', axis=1)

        predictions_binance = model_binance.predict(X_binance)
        prediction_proba_binance = model_binance.predict_proba(X_binance)[:, 1]

        results_df_binance = symbols_binance.loc[X_binance.index].copy()
        results_df_binance['prediction'] = predictions_binance
        results_df_binance['probability_increase'] = prediction_proba_binance
        
        results_binance = results_df_binance.to_dict('records')
        
        return JsonResponse({"predictions": results_binance})

    except FileNotFoundError:
        return JsonResponse({"error": "Binance model or scaler not found. Please train the Binance model first."}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred with Binance predictions: {str(e)}"}, status=500)


# Define the path to the saved artifacts for WazirX
WAZIRX_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "logistic_regression_model_wazirx.joblib")
WAZIRX_SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler_wazirx.joblib")

def predict_wazirx(request):
    """
    API endpoint to get predictions for WazirX cryptocurrencies.
    """
    try:
        model_wazirx = joblib.load(WAZIRX_MODEL_PATH)
        scaler_wazirx = joblib.load(WAZIRX_SCALER_PATH)
        print("WazirX model and scaler loaded successfully.")

        raw_df_wazirx = load_wazirx_data_to_dataframe()
        if raw_df_wazirx.empty:
            return JsonResponse({"error": "Could not load WazirX data from database."}, status=500)
        
        # We need the symbols before they are removed by feature engineering
        symbols_wazirx = raw_df_wazirx[['symbol']].copy()

        processed_df_wazirx, _ = feature_engineer_wazirx(raw_df_wazirx.copy())
        
        if processed_df_wazirx.empty:
            return JsonResponse({"error": "Failed to process WazirX data for prediction."}, status=500)
            
        X_wazirx = processed_df_wazirx.drop('price_will_increase', axis=1)

        predictions_wazirx = model_wazirx.predict(X_wazirx)
        prediction_proba_wazirx = model_wazirx.predict_proba(X_wazirx)[:, 1]

        results_df_wazirx = symbols_wazirx.loc[X_wazirx.index].copy()
        results_df_wazirx['prediction'] = predictions_wazirx
        results_df_wazirx['probability_increase'] = prediction_proba_wazirx
        
        results_wazirx = results_df_wazirx.to_dict('records')
        
        return JsonResponse({"predictions": results_wazirx})

    except FileNotFoundError:
        return JsonResponse({"error": "WazirX model or scaler not found. Please train the WazirX model first."}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred with WazirX predictions: {str(e)}"}, status=500)

def historical_binance_data(request, symbol):
    """
    API endpoint to get historical data for a specific Binance symbol.
    """
    try:
        historical_data = get_historical_binance_data(symbol.upper())
        if not historical_data:
            return JsonResponse({"error": f"No historical data found for symbol {symbol}."}, status=404)
        
        return JsonResponse({"historical_data": historical_data})
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

def historical_wazirx_data(request, symbol):
    """
    API endpoint to get historical data for a specific WazirX symbol.
    """
    try:
        historical_data = get_historical_wazirx_data(symbol.lower() + "inr")
        if not historical_data:
            return JsonResponse({"error": f"No historical data found for symbol {symbol}."}, status=404)
        
        return JsonResponse({"historical_data": historical_data})
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
