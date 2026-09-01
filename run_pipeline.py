"""
End-to-End Pipeline Test Script
Runs the complete demand forecasting pipeline from data preparation to visualization
"""

import subprocess
import sys
import os

def run_step(script_name, description):
    """Run a single step of the pipeline."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print(f"ERROR: {script_name} failed with return code {result.returncode}")
            return False
        
        print(f"[SUCCESS] {description} completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"ERROR: {script_name} timed out")
        return False
    except Exception as e:
        print(f"ERROR: {script_name} failed with exception: {e}")
        return False

def main():
    """Run the complete pipeline."""
    print("="*60)
    print("DEMAND FORECASTING PIPELINE - END-TO-END TEST")
    print("="*60)
    
    steps = [
        ("data_prep.py", "Data Preparation - Load, filter, and clean data"),
        ("forecast_model.py", "Forecasting Model - Train models and generate forecasts"),
        ("demand_signal.py", "Demand Signal Analysis - Calculate demand pressure signals"),
        ("visualize.py", "Visualization - Generate forecast charts")
    ]
    
    results = []
    for script, description in steps:
        success = run_step(script, description)
        results.append((description, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("PIPELINE SUMMARY")
    print(f"{'='*60}")
    
    all_success = True
    for description, success in results:
        status = "[PASSED]" if success else "[FAILED]"
        print(f"{status}: {description}")
        if not success:
            all_success = False
    
    print(f"{'='*60}")
    
    if all_success:
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("\nGenerated files:")
        print("  - cleaned_data.csv (Prepared dataset)")
        print("  - forecasts.csv (Price and activity forecasts)")
        print("  - demand_signals.csv (Demand pressure signals)")
        print("  - onion_forecast.png (Onion price forecast chart)")
        print("  - tomato_forecast.png (Tomato price forecast chart)")
        print("  - comparison_chart.png (Multi-commodity comparison)")
        print("\nTo start the API server, run: python api.py")
        print("Then access: http://localhost:8000/health")
        return 0
    else:
        print("PIPELINE FAILED - Some steps did not complete")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)