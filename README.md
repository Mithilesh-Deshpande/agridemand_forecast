# Agricultural Demand Forecasting Module

A demand forecasting system for agricultural marketplaces that predicts future price/demand trends for crops, helping farmers make informed selling decisions and buyers understand market expectations.

## 🎯 Purpose

This module connects farmers directly with buyers by forecasting agricultural commodity prices and demand signals. It helps farmers know when to sell and buyers understand what to expect in the market.

## 📊 Focus Commodities

- **Onion** - High volatility, easy to explain in demos
- **Tomato** - High volatility, easy to explain in demos

## 🔧 Technical Approach

### Data Proxy
- **Supply Proxy**: Uses market activity count (number of transactions) as a proxy for supply/arrivals
- **Demand Signal**: Price movement serves as the demand indicator
- **Assumption**: Rising price + falling activity = excess demand (High Demand / Sell Now)

### Model Choice
- **Lightweight Forecasting**: Uses exponential smoothing with moving averages instead of Prophet due to disk space constraints
- **Fallback Approach**: Still effective for hackathon demo purposes

## 📁 Project Structure

```
demand_forecasting_module/
├── data_prep.py           # Data loading, filtering, and cleaning
├── forecast_model.py      # Forecasting model (exponential smoothing)
├── demand_signal.py       # Demand pressure signal calculation
├── api.py                 # REST API service
├── visualize.py           # Chart generation
├── run_pipeline.py        # End-to-end pipeline test
├── cleaned_data.csv       # Prepared dataset (generated)
├── forecasts.csv          # Price and activity forecasts (generated)
├── demand_signals.csv     # Demand pressure signals (generated)
├── onion_forecast.png     # Onion forecast chart (generated)
├── tomato_forecast.png    # Tomato forecast chart (generated)
└── comparison_chart.png   # Multi-commodity comparison (generated)
```

## 🚀 Quick Start

### 1. Run the Complete Pipeline
```bash
python run_pipeline.py
```

This will:
- Load and clean the Agmarknet dataset
- Train forecasting models
- Generate 30-day forecasts
- Calculate demand signals
- Create visualization charts

### 2. Start the API Server
```bash
python api.py
```

The API will be available at `http://localhost:8000`

### 3. Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**List Available Commodities:**
```bash
curl http://localhost:8000/commodities
```

**Get Forecast:**
```bash
curl "http://localhost:8000/forecast?commodity=onion&days=14"
```

## 📡 API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-01T06:06:30.239275",
  "service": "Demand Forecasting API"
}
```

### GET /commodities
List available commodities.

**Response:**
```json
{
  "commodities": ["Onion", "Tomato"],
  "count": 2
}
```

### GET /forecast?commodity={commodity}&days={days}
Get forecast for a specific commodity.

**Parameters:**
- `commodity`: Commodity name (onion, tomato)
- `days`: Number of days to forecast (1-90, default: 14)

**Response:**
```json
{
  "commodity": "Onion",
  "forecast_days": 14,
  "generated_at": "2026-09-01T06:06:37.855832",
  "demand_signal": "High Demand / Sell Now",
  "signal_reason": "Price +10.1%, Activity -0.4%",
  "forecasts": [
    {
      "date": "2025-06-12",
      "predicted_price": 2004.68,
      "predicted_activity": 6.26,
      "price_lower": 1703.98,
      "price_upper": 2305.38,
      "demand_signal": "High Demand / Sell Now"
    }
  ]
}
```

## 📈 Demand Signal Logic

The system calculates demand signals based on forecasted price and activity trends:

- **High Demand / Sell Now**: Price rising + Activity falling (excess demand)
- **Low Demand / Hold or Diversify**: Price falling + Activity rising (excess supply)
- **Stable**: Other combinations

## 📊 Visualization

The module generates three types of charts:

1. **Individual Commodity Forecasts** (`onion_forecast.png`, `tomato_forecast.png`)
   - Historical prices (blue line)
   - Forecasted prices (red dashed line)
   - Confidence intervals (red shaded area)
   - Demand signal annotation

2. **Comparison Chart** (`comparison_chart.png`)
   - Side-by-side comparison of multiple commodities
   - Historical and forecasted prices for each

## 🔍 Data Source

Uses the **Agmarknet India Commodity Prices** dataset (October 2024 – August 2025) with over 737,000 records across Indian agricultural markets.

**Columns:**
- State, District Name, Market Name
- Commodity, Variety, Grade
- Min Price, Max Price, Modal Price (Rs./Quintal)
- Price Date

## 🛠️ Individual Module Testing

Test each module separately:

```bash
# Data preparation
python data_prep.py

# Forecasting model
python forecast_model.py

# Demand signal analysis
python demand_signal.py

# Visualization
python visualize.py
```

## 📝 Notes

- **Hackathon Demo**: Prioritized working end-to-end pipeline over production-grade robustness
- **Disk Space Constraints**: Used lightweight libraries (pandas, numpy) instead of Prophet due to installation issues
- **Data Limitations**: Dataset doesn't include explicit "arrivals" data, so market activity count is used as a proxy
- **Forecast Horizon**: Default 30 days, configurable via API

## 🎯 Usage for Hackathon Demo

1. **Show Data Pipeline**: Run `python run_pipeline.py` to demonstrate the complete workflow
2. **Show API**: Start `python api.py` and demonstrate live forecasting
3. **Show Visualizations**: Display the generated PNG charts in your presentation
4. **Explain Logic**: Use the demand signal examples to explain the business value

## 📄 License

This project uses the Agmarknet dataset under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license.