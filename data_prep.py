"""
Data Preparation Module for Agricultural Demand Forecasting
Loads, filters, and cleans the Agmarknet commodity price data for onion and tomato.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_and_filter_data(csv_path, commodities=['Onion', 'Tomato']):
    """
    Load the Agmarknet dataset and filter for specified commodities.
    
    Args:
        csv_path: Path to the Agriculture_price_dataset.csv
        commodities: List of commodities to filter (default: ['Onion', 'Tomato'])
    
    Returns:
        Filtered DataFrame with onion and tomato data
    """
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Total records in dataset: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Filter for specified commodities
    df_filtered = df[df['Commodity'].isin(commodities)].copy()
    print(f"\nRecords after filtering for {commodities}: {len(df_filtered)}")
    
    # Show distribution by commodity
    print(f"\nRecords by commodity:")
    print(df_filtered['Commodity'].value_counts())
    
    return df_filtered

def clean_data(df):
    """
    Clean the data by handling nulls, duplicates, and standardizing formats.
    
    Args:
        df: Filtered DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    print("\nCleaning data...")
    
    # Check for nulls
    print(f"Null values before cleaning:")
    print(df.isnull().sum())
    
    # Drop rows with critical null values (price data)
    df_clean = df.dropna(subset=['Modal_Price', 'Price Date'])
    
    # Remove duplicates
    duplicates_before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    duplicates_removed = duplicates_before - len(df_clean)
    print(f"Removed {duplicates_removed} duplicate records")
    
    # Standardize date format
    df_clean['Price Date'] = pd.to_datetime(df_clean['Price Date'], errors='coerce')
    df_clean = df_clean.dropna(subset=['Price Date'])  # Remove invalid dates
    
    # Sort by date
    df_clean = df_clean.sort_values('Price Date')
    
    print(f"Records after cleaning: {len(df_clean)}")
    print(f"Date range: {df_clean['Price Date'].min()} to {df_clean['Price Date'].max()}")
    
    return df_clean

def select_best_markets(df, top_n=2):
    """
    Select the markets with the most complete data for each commodity.
    
    Args:
        df: Cleaned DataFrame
        top_n: Number of top markets to select per commodity
    
    Returns:
        DataFrame filtered to best markets
    """
    print(f"\nSelecting top {top_n} markets per commodity with most data...")
    
    # Count records per market for each commodity
    market_counts = df.groupby(['Commodity', 'Market Name']).size().reset_index(name='count')
    
    # Get top markets for each commodity
    top_markets = market_counts.groupby('Commodity').apply(
        lambda x: x.nlargest(top_n, 'count')
    ).reset_index(drop=True)
    
    print("Top markets selected:")
    print(top_markets)
    
    # Filter to selected markets
    market_list = top_markets['Market Name'].tolist()
    df_filtered = df[df['Market Name'].isin(market_list)].copy()
    
    print(f"Records after market selection: {len(df_filtered)}")
    
    return df_filtered

def aggregate_to_daily(df):
    """
    Aggregate multiple market records per day into daily time series.
    Uses market activity count as a proxy for supply/arrivals.
    
    NOTE: Since the dataset doesn't have explicit 'arrivals' data, 
    we use the count of market transactions per day as a proxy for supply/activity.
    This is a reasonable assumption for hackathon demo purposes.
    
    Args:
        df: DataFrame with market-level data
    
    Returns:
        Aggregated daily DataFrame with columns: date, commodity, avg_price, activity_count
    """
    print("\nAggregating to daily time series...")
    
    # Group by date and commodity
    daily_data = df.groupby(['Price Date', 'Commodity']).agg({
        'Modal_Price': 'mean',  # Average price across markets
        'Market Name': 'count'  # Count of market records as activity proxy
    }).reset_index()
    
    daily_data.columns = ['date', 'commodity', 'avg_price', 'activity_count']
    daily_data = daily_data.sort_values(['commodity', 'date'])
    
    print(f"Daily records: {len(daily_data)}")
    print(f"Date range: {daily_data['date'].min()} to {daily_data['date'].max()}")
    
    return daily_data

def handle_missing_dates(df, max_gap=7):
    """
    Handle missing dates by forward-filling (common for mandi closures on weekends/holidays).
    
    Args:
        df: Daily aggregated DataFrame
        max_gap: Maximum gap to forward-fill (in days)
    
    Returns:
        DataFrame with complete daily time series
    """
    print("\nHandling missing dates...")
    
    complete_data = []
    
    for commodity in df['commodity'].unique():
        commodity_df = df[df['commodity'] == commodity].copy()
        
        # Create complete date range
        date_range = pd.date_range(
            start=commodity_df['date'].min(),
            end=commodity_df['date'].max(),
            freq='D'
        )
        
        # Reindex to complete date range
        commodity_df = commodity_df.set_index('date')
        commodity_df = commodity_df.reindex(date_range)
        
        # Forward fill with limit (respecting max_gap)
        commodity_df['avg_price'] = commodity_df['avg_price'].ffill(limit=max_gap)
        commodity_df['activity_count'] = commodity_df['activity_count'].ffill(limit=max_gap)
        
        # Backward fill for any remaining gaps at the start
        commodity_df['avg_price'] = commodity_df['avg_price'].bfill()
        commodity_df['activity_count'] = commodity_df['activity_count'].bfill()
        
        # Drop any remaining nulls
        commodity_df = commodity_df.dropna()
        
        # Reset index and add commodity back
        commodity_df = commodity_df.reset_index()
        commodity_df = commodity_df[['index', 'avg_price', 'activity_count']]
        commodity_df.columns = ['date', 'avg_price', 'activity_count']
        commodity_df['commodity'] = commodity
        
        complete_data.append(commodity_df)
    
    df_complete = pd.concat(complete_data, ignore_index=True)
    df_complete = df_complete.sort_values(['commodity', 'date'])
    
    print(f"Records after handling missing dates: {len(df_complete)}")
    
    return df_complete

def save_cleaned_data(df, output_path='cleaned_data.csv'):
    """
    Save the cleaned and processed data to CSV.
    
    Args:
        df: Final cleaned DataFrame
        output_path: Path to save the CSV
    """
    df.to_csv(output_path, index=False)
    print(f"\nCleaned data saved to {output_path}")
    print(f"Final dataset shape: {df.shape}")
    print(f"Final columns: {df.columns.tolist()}")

def main():
    """Main execution function."""
    # Configuration
    input_csv = r"C:\Users\Mithilesh\Downloads\extracted_dataset\Agriculture_price_dataset.csv"
    output_csv = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\cleaned_data.csv"
    
    # Step 1: Load and filter
    df = load_and_filter_data(input_csv, commodities=['Onion', 'Tomato'])
    
    # Step 2: Clean data
    df = clean_data(df)
    
    # Step 3: Select best markets
    df = select_best_markets(df, top_n=2)
    
    # Step 4: Aggregate to daily
    df = aggregate_to_daily(df)
    
    # Step 5: Handle missing dates
    df = handle_missing_dates(df)
    
    # Step 6: Save cleaned data
    save_cleaned_data(df, output_csv)
    
    # Display sample of final data
    print("\nSample of cleaned data:")
    print(df.head(10))
    print(f"\nData summary by commodity:")
    print(df.groupby('commodity').agg({
        'date': ['min', 'max', 'count'],
        'avg_price': ['mean', 'std', 'min', 'max'],
        'activity_count': ['mean', 'sum']
    }))

if __name__ == "__main__":
    main()