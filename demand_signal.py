"""
Demand Signal Logic Module
Analyzes forecasted price and activity trends to generate demand pressure signals.
"""

import pandas as pd
import numpy as np

def calculate_demand_signals(forecasts_df):
    """
    Calculate demand signals based on forecasted price and activity trends.
    
    DEMAND SIGNAL LOGIC:
    - Price rising + Activity falling = High Demand / Sell Now (excess demand)
    - Price falling + Activity rising = Low Demand / Hold or Diversify (excess supply)
    - Otherwise = Stable
    
    NOTE: We use 'activity_count' as a proxy for supply/arrivals since the dataset
    doesn't have explicit arrivals data. Higher activity typically indicates higher supply.
    
    Args:
        forecasts_df: DataFrame with forecasted data (from forecast_model.py)
    
    Returns:
        DataFrame with added demand_signal column
    """
    print("Calculating demand signals...")
    
    results = []
    
    for commodity in forecasts_df['commodity'].unique():
        commodity_forecast = forecasts_df[forecasts_df['commodity'] == commodity].copy()
        commodity_forecast = commodity_forecast.sort_values('date')
        
        # Calculate trends (compare first week to last week of forecast)
        if len(commodity_forecast) >= 14:
            first_week_price = commodity_forecast['predicted_price'].head(7).mean()
            last_week_price = commodity_forecast['predicted_price'].tail(7).mean()
            
            first_week_activity = commodity_forecast['predicted_activity'].head(7).mean()
            last_week_activity = commodity_forecast['predicted_activity'].tail(7).mean()
            
            price_trend = 'up' if last_week_price > first_week_price else 'down'
            activity_trend = 'up' if last_week_activity > first_week_activity else 'down'
            
            # Calculate percentage changes
            price_change_pct = ((last_week_price - first_week_price) / first_week_price) * 100
            activity_change_pct = ((last_week_activity - first_week_activity) / first_week_activity) * 100
            
            # Apply demand signal logic
            if price_trend == 'up' and activity_trend == 'down':
                demand_signal = "High Demand / Sell Now"
                signal_reason = f"Price +{price_change_pct:.1f}%, Activity {activity_change_pct:.1f}%"
            elif price_trend == 'down' and activity_trend == 'up':
                demand_signal = "Low Demand / Hold or Diversify"
                signal_reason = f"Price {price_change_pct:.1f}%, Activity +{activity_change_pct:.1f}%"
            else:
                demand_signal = "Stable"
                signal_reason = f"Price {price_change_pct:+.1f}%, Activity {activity_change_pct:+.1f}%"
        else:
            # Not enough data for trend analysis
            demand_signal = "Stable"
            signal_reason = "Insufficient forecast data"
        
        # Apply the same signal to all days in the forecast for this commodity
        commodity_forecast['demand_signal'] = demand_signal
        commodity_forecast['signal_reason'] = signal_reason
        
        results.append(commodity_forecast)
    
    final_df = pd.concat(results, ignore_index=True)
    
    # Display summary
    print("\nDemand Signal Summary:")
    for commodity in final_df['commodity'].unique():
        commodity_data = final_df[final_df['commodity'] == commodity]
        signal = commodity_data['demand_signal'].iloc[0]
        reason = commodity_data['signal_reason'].iloc[0]
        print(f"  {commodity}: {signal} ({reason})")
    
    return final_df

def generate_demand_report(forecasts_df, output_path='demand_signals.csv'):
    """
    Generate a comprehensive demand report with key metrics.
    
    Args:
        forecasts_df: DataFrame with forecasted data and demand signals
        output_path: Path to save the demand report CSV
    """
    print(f"\nGenerating demand report...")
    
    # Create summary table
    summary_data = []
    
    for commodity in forecasts_df['commodity'].unique():
        commodity_data = forecasts_df[forecasts_df['commodity'] == commodity]
        
        avg_forecasted_price = commodity_data['predicted_price'].mean()
        avg_forecasted_activity = commodity_data['predicted_activity'].mean()
        price_volatility = commodity_data['predicted_price'].std()
        demand_signal = commodity_data['demand_signal'].iloc[0]
        signal_reason = commodity_data['signal_reason'].iloc[0]
        
        summary_data.append({
            'commodity': commodity,
            'avg_forecasted_price': round(avg_forecasted_price, 2),
            'avg_forecasted_activity': round(avg_forecasted_activity, 2),
            'price_volatility': round(price_volatility, 2),
            'demand_signal': demand_signal,
            'signal_reason': signal_reason
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save detailed forecast with signals
    output_columns = ['date', 'commodity', 'predicted_price', 'predicted_activity', 
                     'price_lower', 'price_upper', 'demand_signal', 'signal_reason']
    forecasts_df[output_columns].to_csv(output_path, index=False)
    
    print(f"Demand signals saved to {output_path}")
    
    return summary_df

def main():
    """Main execution function."""
    # Configuration
    forecasts_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\forecasts.csv"
    output_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\demand_signals.csv"
    
    # Load forecasts
    print(f"Loading forecasts from {forecasts_path}...")
    forecasts_df = pd.read_csv(forecasts_path)
    forecasts_df['date'] = pd.to_datetime(forecasts_df['date'])
    
    print(f"Loaded {len(forecasts_df)} forecast records")
    print(f"Commodities: {forecasts_df['commodity'].unique()}")
    
    # Calculate demand signals
    signals_df = calculate_demand_signals(forecasts_df)
    
    # Generate and save demand report
    summary_df = generate_demand_report(signals_df, output_path)
    
    print("\nDemand Signal Summary Table:")
    print(summary_df.to_string(index=False))
    
    # Show sample of detailed signals
    print("\nSample detailed signals (first 10 rows):")
    print(signals_df[['date', 'commodity', 'predicted_price', 'predicted_activity', 'demand_signal']].head(10))
    
    print(f"\nDemand signal analysis complete!")

if __name__ == "__main__":
    main()