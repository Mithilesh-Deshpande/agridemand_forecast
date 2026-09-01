"""
Visualization Module for Demand Forecasting
Creates charts showing historical + forecasted prices with demand signals
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

def plot_forecast_with_signals(cleaned_data_path, signals_path, commodity='Onion', output_path='forecast_chart.png'):
    """
    Create a chart showing historical prices and forecasted prices with demand signals.
    
    Args:
        cleaned_data_path: Path to cleaned_data.csv (historical data)
        signals_path: Path to demand_signals.csv (forecasted data with signals)
        commodity: Commodity to visualize
        output_path: Path to save the chart
    """
    print(f"Creating visualization for {commodity}...")
    
    # Load historical data
    historical_df = pd.read_csv(cleaned_data_path)
    historical_df['date'] = pd.to_datetime(historical_df['date'])
    historical_df = historical_df[historical_df['commodity'] == commodity].sort_values('date')
    
    # Load forecast data with signals
    forecast_df = pd.read_csv(signals_path)
    forecast_df['date'] = pd.to_datetime(forecast_df['date'])
    forecast_df = forecast_df[forecast_df['commodity'] == commodity].sort_values('date')
    
    # Get the demand signal for this commodity
    if len(forecast_df) > 0:
        demand_signal = forecast_df['demand_signal'].iloc[0]
        signal_color = 'green' if 'High Demand' in demand_signal else ('red' if 'Low Demand' in demand_signal else 'orange')
    else:
        demand_signal = 'Unknown'
        signal_color = 'gray'
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot historical prices
    ax.plot(historical_df['date'], historical_df['avg_price'], 
            label='Historical Price', color='blue', linewidth=2, alpha=0.7)
    
    # Plot forecasted prices
    ax.plot(forecast_df['date'], forecast_df['predicted_price'], 
            label='Forecasted Price', color='red', linewidth=2, linestyle='--')
    
    # Plot confidence intervals
    ax.fill_between(forecast_df['date'], 
                     forecast_df['price_lower'], 
                     forecast_df['price_upper'],
                     alpha=0.2, color='red', label='Confidence Interval')
    
    # Add vertical line at forecast start
    if len(historical_df) > 0 and len(forecast_df) > 0:
        forecast_start = forecast_df['date'].min()
        ax.axvline(x=forecast_start, color='black', linestyle=':', linewidth=2, 
                  label='Forecast Start')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Price (Rs./Quintal)', fontsize=12, fontweight='bold')
    ax.set_title(f'{commodity} Price Forecast - {demand_signal}', 
                fontsize=14, fontweight='bold', color=signal_color)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Add demand signal annotation
    if len(forecast_df) > 0:
        avg_forecast_price = forecast_df['predicted_price'].mean()
        ax.text(0.02, 0.98, f'Demand Signal: {demand_signal}', 
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor=signal_color, alpha=0.3))
        
        # Add forecast statistics
        stats_text = f"Avg Forecast: ₹{avg_forecast_price:.0f}/Q\n"
        stats_text += f"Forecast Days: {len(forecast_df)}\n"
        stats_text += f"Price Range: ₹{forecast_df['predicted_price'].min():.0f} - ₹{forecast_df['predicted_price'].max():.0f}/Q"
        
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Tight layout
    plt.tight_layout()
    
    # Save the chart
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")
    
    # Close the plot
    plt.close()
    
    return output_path

def plot_multi_commodity_comparison(cleaned_data_path, signals_path, output_path='comparison_chart.png'):
    """
    Create a comparison chart showing multiple commodities.
    
    Args:
        cleaned_data_path: Path to cleaned_data.csv
        signals_path: Path to demand_signals.csv
        output_path: Path to save the comparison chart
    """
    print("Creating multi-commodity comparison chart...")
    
    # Load data
    historical_df = pd.read_csv(cleaned_data_path)
    historical_df['date'] = pd.to_datetime(historical_df['date'])
    
    forecast_df = pd.read_csv(signals_path)
    forecast_df['date'] = pd.to_datetime(forecast_df['date'])
    
    # Get unique commodities
    commodities = historical_df['commodity'].unique()
    
    # Create subplots
    fig, axes = plt.subplots(len(commodities), 1, figsize=(14, 6*len(commodities)))
    if len(commodities) == 1:
        axes = [axes]
    
    for idx, commodity in enumerate(commodities):
        ax = axes[idx]
        
        # Get historical data
        hist_data = historical_df[historical_df['commodity'] == commodity].sort_values('date')
        
        # Get forecast data
        fore_data = forecast_df[forecast_df['commodity'] == commodity].sort_values('date')
        
        # Get signal color
        if len(fore_data) > 0:
            demand_signal = fore_data['demand_signal'].iloc[0]
            signal_color = 'green' if 'High Demand' in demand_signal else ('red' if 'Low Demand' in demand_signal else 'orange')
        else:
            demand_signal = 'Unknown'
            signal_color = 'gray'
        
        # Plot historical
        ax.plot(hist_data['date'], hist_data['avg_price'], 
               label='Historical', color='blue', linewidth=2, alpha=0.7)
        
        # Plot forecast
        if len(fore_data) > 0:
            ax.plot(fore_data['date'], fore_data['predicted_price'], 
                   label='Forecast', color='red', linewidth=2, linestyle='--')
            ax.fill_between(fore_data['date'], 
                           fore_data['price_lower'], 
                           fore_data['price_upper'],
                           alpha=0.2, color='red')
            
            # Add forecast start line
            forecast_start = fore_data['date'].min()
            ax.axvline(x=forecast_start, color='black', linestyle=':', linewidth=2)
        
        # Styling
        ax.set_ylabel('Price (Rs./Quintal)', fontsize=10, fontweight='bold')
        ax.set_title(f'{commodity} - {demand_signal}', fontsize=12, fontweight='bold', color=signal_color)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=9)
        
        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Comparison chart saved to {output_path}")
    plt.close()
    
    return output_path

def main():
    """Main execution function."""
    # Configuration
    cleaned_data_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\cleaned_data.csv"
    signals_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\demand_signals.csv"
    
    # Create individual charts for each commodity
    commodities = ['Onion', 'Tomato']
    
    for commodity in commodities:
        output_path = f"C:\\Users\\Mithilesh\\Desktop\\Backup mithilesh\\demand_forecasting_module\\{commodity.lower()}_forecast.png"
        plot_forecast_with_signals(cleaned_data_path, signals_path, commodity, output_path)
    
    # Create comparison chart
    comparison_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\comparison_chart.png"
    plot_multi_commodity_comparison(cleaned_data_path, signals_path, comparison_path)
    
    print("\nVisualization complete!")
    print("Generated charts:")
    print("  - onion_forecast.png")
    print("  - tomato_forecast.png")
    print("  - comparison_chart.png")

if __name__ == "__main__":
    main()