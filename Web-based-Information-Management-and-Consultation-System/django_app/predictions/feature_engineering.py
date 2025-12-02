import pandas as pd
from sklearn.preprocessing import StandardScaler

def get_cleaned_data():
    """
    This function will eventually load data from MongoDB, but for now,
    it assumes the data is already loaded into a pandas DataFrame.
    This function will be expanded later to call the pymongo loading logic.
    For now, it returns an empty DataFrame to avoid errors if called directly.
    """
    # This part will be completed later to integrate with the pymongo loader
    # For now, we will create a dummy function to represent the data loading
    # and call it from the main feature engineering function.
    return pd.DataFrame()

def feature_engineer(df):
    """
    Performs feature engineering and preprocessing on the raw cryptocurrency data.

    Args:
        df (pd.DataFrame): The raw cryptocurrency data.

    Returns:
        tuple: A tuple containing the processed DataFrame and the fitted scaler object.
    """
    if df.empty:
        print("Input DataFrame is empty. Cannot perform feature engineering.")
        return pd.DataFrame(), None

    print("Starting feature engineering...")

    # 1. Define Prediction Target
    df['price_will_increase'] = (df['price_change_percentage_24h'] > 0).astype(int)
    print("Created target variable 'price_will_increase'.")

    # 2. Handle Duplicate Symbols
    df.sort_values('market_cap', ascending=False, inplace=True)
    df.drop_duplicates(subset='symbol', keep='first', inplace=True)
    print(f"Handled duplicate symbols. Kept highest market cap. New shape: {df.shape}")

    # 3. Data Cleaning
    # Convert date columns to datetime
    df['ath_date'] = pd.to_datetime(df['ath_date'])
    df['atl_date'] = pd.to_datetime(df['atl_date'])
    print("Converted date columns to datetime objects.")
    
    # Drop max_supply for now
    df.drop(columns=['max_supply'], inplace=True)
    print("Dropped 'max_supply' column.")

    # 4. Feature Selection
    features_to_use = [
        'current_price', 
        'market_cap', 
        'total_volume', 
        'circulating_supply',
        'price_change_24h',
        'price_change_percentage_24h',
        'high_24h',
        'low_24h',
        'ath',
        'atl'
    ]
    
    target = 'price_will_increase'
    
    # Create a new DataFrame with selected features and the target
    processed_df = df[features_to_use + [target]].copy()
    
    # Drop rows with any remaining NaN values (if any)
    processed_df.dropna(inplace=True)
    print(f"Selected features and dropped NaNs. New shape: {processed_df.shape}")

    # 5. Feature Scaling
    scaler = StandardScaler()
    # Only scale the features, not the target
    processed_df[features_to_use] = scaler.fit_transform(processed_df[features_to_use])
    print("Scaled numerical features using StandardScaler.")

    print("Feature engineering complete.")
    return processed_df, scaler
if __name__ == '__main__':
    # To test this script, we need data. We will call the pymongo loader from eda_script.
    # For now, this part is for demonstration.
    # In the next step, we will integrate this with the data loader.
    print("This script is for feature engineering. It needs to be integrated with a data loader.")
    # Example of how it would be used:
    # from eda_script import load_data_to_dataframe
    # raw_df = load_data_to_dataframe()
    # processed_data = feature_engineer(raw_df)
    # if not processed_data.empty:
    #     print("\n--- Processed DataFrame Head ---")
    #     print(processed_data.head())
