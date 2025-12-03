import pandas as pd
from sklearn.preprocessing import StandardScaler

def feature_engineer_binance(df):
    """
    Performs feature engineering and preprocessing on the raw Binance ticker data.

    Args:
        df (pd.DataFrame): The raw Binance ticker data.

    Returns:
        tuple: A tuple containing the processed DataFrame and the fitted scaler object.
    """
    if df.empty:
        print("Input DataFrame is empty. Cannot perform feature engineering.")
        return pd.DataFrame(), None

    print("Starting feature engineering for Binance data...")

    # 1. Define Prediction Target
    df['price_will_increase'] = (df['price_change_percent'] > 0).astype(int)
    print("Created target variable 'price_will_increase'.")

    # 2. Data Cleaning
    # Convert date columns to datetime
    df['open_time'] = pd.to_datetime(df['open_time'])
    df['close_time'] = pd.to_datetime(df['close_time'])
    print("Converted date columns to datetime objects.")
    
    # 3. Feature Selection
    features_to_use = [
        'price_change',
        'price_change_percent',
        'last_price',
        'open_price',
        'high_price',
        'low_price',
        'bid_price',
        'bid_qty',
        'ask_price',
        'ask_qty',
        'volume_base',
        'volume_quote',
        'trade_count'
    ]
    
    target = 'price_will_increase'
    
    # Create a new DataFrame with selected features and the target
    processed_df = df[features_to_use + [target]].copy()
    
    # Drop rows with any remaining NaN values (if any)
    processed_df.dropna(inplace=True)
    print(f"Selected features and dropped NaNs. New shape: {processed_df.shape}")

    # 4. Feature Scaling
    scaler = StandardScaler()
    # Only scale the features, not the target
    processed_df[features_to_use] = scaler.fit_transform(processed_df[features_to_use])
    print("Scaled numerical features using StandardScaler.")

    print("Feature engineering for Binance data complete.")
    return processed_df, scaler
