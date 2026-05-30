import time
import os
from train import execute_ml_pipeline

def run_continuous_loop():
    # Set interval cycles (e.g., check and refresh every 60 seconds)
    CHECK_INTERVAL_SECONDS = 60
    
    print("🚀 MLOps Orchestrator Started! Monitoring market changes automatically...")
    
    while True:
        try:
            print(f"\n⏰ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Launching automated ingestion and training run...")
            
            # Execute data compilation and model optimization matching loop
            execute_ml_pipeline()
            
            print(f"😴 Run complete. Sleeping for {CHECK_INTERVAL_SECONDS} seconds before next evaluation.")
            time.sleep(CHECK_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\nStopping orchestrator engine safely.")
            break
        except Exception as e:
            print(f"Orchestrator error encountered: {e}")
            time.sleep(10) # Pause before trying again

if __name__ == "__main__":
    run_continuous_loop()