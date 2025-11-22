import argparse
import json
import boto3
import time
import os
from datetime import datetime

# Defaults
DEFAULT_PROJECT = "CoolGroup"
DEFAULT_ENV = "dev"
DEFAULT_REGION = "eu-central-1"

def get_lambda_client(region):
    return boto3.client('lambda', region_name=region)

def generate_environment_payload(scenario, user_id):
    base_ts = int(datetime.now().timestamp() * 1000)
    
    payload = {
        "user_id": user_id,
        "batch": []
    }
    
    if scenario == "hike":
        # High Altitude, Lower Pressure, Moderate HR, Walking
        data = {
            "timestamp": base_ts,
            "vitals": {
                "heartRate": 110,
                "spo2": 95.0 # Lower due to altitude?
            },
            "environment": {
                "altitude": 2500.0, # 2500m
                "barometer": 750.0, # Low pressure
                "ambientLight": 50000, # Sunny
                "location": { "latitude": 47.42, "longitude": 10.98 } # Alps
            },
            "activity": {
                "stepCount": 5000,
                "isIntensity": True
            }
        }
        
    elif scenario == "commute":
        # High Speed, No Steps, Stress?
        data = {
            "timestamp": base_ts,
            "vitals": {
                "heartRate": 85, # Slightly elevated
                "stressScore": 60
            },
            "environment": {
                "altitude": 500.0,
                "location": { "latitude": 48.13, "longitude": 11.58 } # Munich
            },
            "activity": {
                "stepCount": 0,
                "speed": 15.0, # 54 km/h (Car/Bus)
                "distance": 5000
            }
        }
        
    elif scenario == "fever":
        # High Body Temp, Resting High HR
        data = {
            "timestamp": base_ts,
            "vitals": {
                "heartRate": 90, # Resting high
                "bodyTemperature": 38.5, # Fever
                "skinTemperature": 37.8
            },
            "body": {
                "weight": 75.0
            },
            "activity": {
                "stepCount": 0,
                "isIntensity": False
            },
            "wellbeing": {
                "sleepScore": 40,
                "emotionStatus": 1 # Unpleasant
            }
        }
    
    else:
        raise ValueError("Unknown scenario")

    # Wrap in the flat structure expected by the simplified ingest if needed, 
    # OR strictly adhere to the complex schema if ingest handles it.
    # The current ingest 'sensor_ingest.py' just stores what it gets.
    # But the 'State Reactor' might expect flattened keys or specific paths.
    # For this demo, we'll flatten the critical keys for the simple 'State Reactor' 
    # but keep the complex structure for future advanced parsers.
    
    # Hybrid approach: Flat keys for current logic + Complex object for future
    flat_data = {
        "timestamp": data["timestamp"],
        "heartRate": data["vitals"].get("heartRate"),
        "step_count": data["activity"].get("stepCount"),
        "stress_score": data["vitals"].get("stressScore"),
        "body_temp": data["vitals"].get("bodyTemperature"),
        "altitude": data["environment"].get("altitude") if "environment" in data else None,
        # Store full complex object too
        "raw_complex": data
    }
    
    payload["batch"].append(flat_data)
    return payload

def run_simulation(args):
    client = get_lambda_client(args.region)
    ingest_func = args.ingest_func or f"{args.project}-ingest-{args.env}"
    
    print(f"--- Environment Simulator: {args.scenario.upper()} ---")
    print(f"Injecting to: {ingest_func}")
    
    payload = generate_environment_payload(args.scenario, args.user_id)
    
    try:
        response = client.invoke(
            FunctionName=ingest_func,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        print(f"Response: {response['Payload'].read()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject Environmental Context")
    parser.add_argument("--scenario", type=str, choices=["hike", "commute", "fever"], required=True)
    parser.add_argument("--user_id", type=str, default="demo_user")
    parser.add_argument("--project", type=str, default=DEFAULT_PROJECT)
    parser.add_argument("--env", type=str, default=DEFAULT_ENV)
    parser.add_argument("--region", type=str, default=DEFAULT_REGION)
    parser.add_argument("--ingest-func", type=str)
    
    args = parser.parse_args()
    run_simulation(args)
