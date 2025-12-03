import pandas as pd
from sklearn.preprocessing import StandardScaler

def feature_engineer_wazirx(df):
    """
    Performs feature engineering and preprocessing on the raw WazirX ticker data.

    Args:
        df (pd.DataFrame): The raw WazirX ticker data.

    Returns:
        tuple: A tuple containing the processed DataFrame and the fitted scaler object.
    """
    if df.empty:
        print("Input DataFrame is empty. Cannot perform feature engineering.")
        return pd.DataFrame(), None

    print("Starting feature engineering for WazirX data...")

    # 1. Calculate price_change_percent
    df['price_change_percent'] = ((df['last_price'] - df['open_price']) / df['open_price']) * 100
    print("Calculated 'price_change_percent'.")

    # 2. Define Prediction Target
    df['price_will_increase'] = (df['price_change_percent'] > 0).astype(int)
    print("Created target variable 'price_will_increase'.")

    # 3. Data Cleaning
    # Convert date columns to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print("Converted date columns to datetime objects.")
    
    # 4. Feature Selection
    features_to_use = [
        'open_price',
        'last_price',
        'high_price',
        'low_price',
        'volume',
        'bid_price',
        'ask_price',
        'price_change_percent'
    ]
    
    target = 'price_will_increase'
    
    # Create a new DataFrame with selected features and the target
    processed_df = df[features_to_use + [target]].copy()
    
    # Drop rows with any remaining NaN values (if any)
    processed_df.dropna(inplace=True)
    # Replace infinite values with NaN and drop them
    processed_df.replace([float('inf'), float('-inf')], pd.NA, inplace=True)
    processed_df.dropna(inplace=True)
    
    print(f"Selected features and dropped NaNs/Infs. New shape: {processed_df.shape}")

    # 5. Feature Scaling
    scaler = StandardScaler()
    # Only scale the features, not the target
    processed_df[features_to_use] = scaler.fit_transform(processed_df[features_to_use])
    print("Scaled numerical features using StandardScaler.")

    print("Feature engineering for WazirX data complete.")
    return processed_df, scaler
