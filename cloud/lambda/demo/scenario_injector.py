import argparse
import json
import boto3
import time
import os
from datetime import datetime
import random

# Defaults
DEFAULT_PROJECT = "CoolGroup"
DEFAULT_ENV = "dev"
DEFAULT_REGION = "eu-central-1"

def get_lambda_client(region):
    return boto3.client('lambda', region_name=region)

def generate_payload(scenario, user_id):
    base_ts = int(datetime.now().timestamp() * 1000)
    
    if scenario == "stress":
        # High HR, Low Movement
        return {
            "user_id": user_id,
            "batch": [
                {
                    "timestamp": base_ts - 1000,
                    "heartRate": 115,
                    "accelerometer": {"x": 0.01, "y": 0.02, "z": 0.98}, # Stationary
                    "stress_score": 85
                },
                {
                    "timestamp": base_ts,
                    "heartRate": 120,
                    "accelerometer": {"x": 0.01, "y": 0.01, "z": 0.99},
                    "stress_score": 88
                }
            ]
        }
    
    elif scenario == "workout":
        # High HR, High Movement
        return {
            "user_id": user_id,
            "batch": [
                {
                    "timestamp": base_ts - 1000,
                    "heartRate": 145,
                    "accelerometer": {"x": 1.2, "y": 0.8, "z": 0.5}, # Active
                    "activity_type": "RUNNING"
                },
                {
                    "timestamp": base_ts,
                    "heartRate": 150,
                    "accelerometer": {"x": 1.3, "y": 0.9, "z": 0.6},
                    "activity_type": "RUNNING"
                }
            ]
        }

    elif scenario == "sleep":
        # Low HR, No Movement
        return {
            "user_id": user_id,
            "batch": [
                {
                    "timestamp": base_ts - 1000,
                    "heartRate": 55,
                    "accelerometer": {"x": 0.0, "y": 0.0, "z": 1.0},
                    "sleep_status": "ASLEEP"
                },
                {
                    "timestamp": base_ts,
                    "heartRate": 54,
                    "accelerometer": {"x": 0.0, "y": 0.0, "z": 1.0},
                    "sleep_status": "ASLEEP"
                }
            ]
        }
        
    elif scenario == "normal":
        return {
            "user_id": user_id,
            "batch": [
                {
                    "timestamp": base_ts,
                    "heartRate": 72,
                    "accelerometer": {"x": 0.1, "y": 0.2, "z": 0.9},
                    "step_count": 12
                }
            ]
        }

    else:
        raise ValueError(f"Unknown scenario: {scenario}")

def run_scenario(args):
    client = get_lambda_client(args.region)
    
    # 1. Determine Function Names
    ingest_func = args.ingest_func or f"{args.project}-ingest-{args.env}"
    orch_func = args.orch_func or f"{args.project}-orchestrator-{args.env}"
    
    print(f"--- Scenario Injector: {args.scenario.upper()} ---")
    print(f"Targeting User: {args.user_id}")
    print(f"Ingest Function: {ingest_func}")
    print(f"Orchestrator Function: {orch_func}")
    
    # 2. Generate & Send Data
    payload = generate_payload(args.scenario, args.user_id)
    print("\n[1/2] Injecting Sensor Data...")
    try:
        response = client.invoke(
            FunctionName=ingest_func,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        resp_payload = json.loads(response['Payload'].read())
        print(f"      Result: {resp_payload}")
    except Exception as e:
        print(f"      Error injecting data: {e}")
        return

    # 3. Trigger Orchestrator directly to see the result
    # (Ingest triggers it async, but we want to see the output synchronously for the demo)
    print("\n[2/2] Invoking Orchestrator for Immediate Reaction...")
    
    orch_payload = {
        "user_id": args.user_id,
        "trigger": "demo_manual_invoke",
        "source": "demo_script", # Force state reactor path
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    
    try:
        start_time = time.time()
        response = client.invoke(
            FunctionName=orch_func,
            InvocationType='RequestResponse',
            Payload=json.dumps(orch_payload)
        )
        end_time = time.time()
        
        resp_payload = json.loads(response['Payload'].read())
        print(f"\n>>> ORCHESTRATOR RESPONSE ({end_time - start_time:.2f}s) <<<")
        print(json.dumps(resp_payload, indent=2))
        
        if 'body' in resp_payload:
            try:
                body = json.loads(resp_payload['body'])
                if 'new_state' in body:
                    print(f"\n>>> PET STATE CHANGED TO: {body['new_state']} <<<")
                    print(f"Reasoning: {body.get('reasoning')}")
            except:
                pass

    except Exception as e:
        print(f"      Error invoking orchestrator: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject scenarios into the AI Tamagotchi Cloud")
    parser.add_argument("--scenario", type=str, choices=["stress", "workout", "sleep", "normal"], required=True, help="The scenario to simulate")
    parser.add_argument("--user_id", type=str, default="demo_user", help="User ID to target")
    parser.add_argument("--project", type=str, default=DEFAULT_PROJECT, help="Project name prefix")
    parser.add_argument("--env", type=str, default=DEFAULT_ENV, help="Environment (dev, prod)")
    parser.add_argument("--region", type=str, default=DEFAULT_REGION, help="AWS Region")
    parser.add_argument("--ingest-func", type=str, help="Override ingest function name")
    parser.add_argument("--orch-func", type=str, help="Override orchestrator function name")
    
    args = parser.parse_args()
    run_scenario(args)
