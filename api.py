"""
Simple API Service for Demand Forecasting
Uses Python's built-in http.server for a lightweight REST API
(Alternative to FastAPI due to disk space constraints)
"""

import json
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import forecast_model
import demand_signal
import datetime

class ForecastAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for forecast API."""
    
    def _set_headers(self, status_code=200):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response."""
        self._set_headers(status_code)
        response = json.dumps(data, default=str)
        self.wfile.write(response.encode())
    
    def _send_error(self, message, status_code=400):
        """Send error response."""
        self._send_json_response({'error': message}, status_code)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Health check endpoint
        if path == '/health':
            self._send_json_response({
                'status': 'healthy',
                'timestamp': datetime.datetime.now().isoformat(),
                'service': 'Demand Forecasting API'
            })
            return
        
        # Forecast endpoint
        if path == '/forecast':
            try:
                # Get query parameters
                commodity = query_params.get('commodity', ['onion'])[0].lower()
                days = int(query_params.get('days', ['14'])[0])
                
                # Validate parameters
                if days < 1 or days > 90:
                    self._send_error('days must be between 1 and 90', 400)
                    return
                
                # Load and process data
                cleaned_data_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\cleaned_data.csv"
                
                # Train model and generate forecast
                _, forecaster = forecast_model.train_and_forecast(cleaned_data_path, forecast_days=days)
                
                # Get forecast for specific commodity
                commodity_capitalized = commodity.capitalize()
                if commodity_capitalized not in forecaster.models:
                    available = list(forecaster.models.keys())
                    self._send_error(f'Commodity {commodity} not found. Available: {available}', 404)
                    return
                
                forecast_df = forecaster.forecast(commodity_capitalized, days=days)
                forecast_df['commodity'] = commodity_capitalized
                
                # Calculate demand signals
                signals_df = demand_signal.calculate_demand_signals(forecast_df)
                
                # Format response
                response_data = {
                    'commodity': commodity_capitalized,
                    'forecast_days': days,
                    'generated_at': datetime.datetime.now().isoformat(),
                    'demand_signal': signals_df['demand_signal'].iloc[0],
                    'signal_reason': signals_df['signal_reason'].iloc[0],
                    'forecasts': []
                }
                
                for _, row in signals_df.iterrows():
                    response_data['forecasts'].append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'predicted_price': round(row['predicted_price'], 2),
                        'predicted_activity': round(row['predicted_activity'], 2),
                        'price_lower': round(row['price_lower'], 2),
                        'price_upper': round(row['price_upper'], 2),
                        'demand_signal': row['demand_signal']
                    })
                
                self._send_json_response(response_data)
                
            except Exception as e:
                self._send_error(f'Internal server error: {str(e)}', 500)
                return
        
        # List available commodities endpoint
        if path == '/commodities':
            try:
                cleaned_data_path = r"C:\Users\Mithilesh\Desktop\Backup mithilesh\demand_forecasting_module\cleaned_data.csv"
                df = pd.read_csv(cleaned_data_path)
                commodities = df['commodity'].unique().tolist()
                
                self._send_json_response({
                    'commodities': commodities,
                    'count': len(commodities)
                })
            except Exception as e:
                self._send_error(f'Error loading commodities: {str(e)}', 500)
            return
        
        # 404 for unknown paths
        self._send_error('Endpoint not found', 404)
    
    def log_message(self, format, *args):
        """Custom log message to reduce console noise."""
        # Only log important messages
        if 'GET /forecast' in format or 'GET /health' in format:
            print(f"[API] {format % args}")

def run_server(host='localhost', port=8000):
    """
    Run the HTTP server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, ForecastAPIHandler)
    
    print(f"Starting Demand Forecasting API server...")
    print(f"Server running at http://{host}:{port}")
    print(f"Available endpoints:")
    print(f"  GET /health - Health check")
    print(f"  GET /commodities - List available commodities")
    print(f"  GET /forecast?commodity=onion&days=14 - Get forecast")
    print(f"\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()