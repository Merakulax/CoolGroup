"""
Sensor Ingestion Lambda
Receives batched sensor data from phone bridge and stores in DynamoDB.
Triggers the Orchestrator asynchronously.
"""

import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

# Clients
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

# Resources
health_table = dynamodb.Table(os.environ.get('HEALTH_TABLE', 'health_data'))

def handler(event, context):
    """
    Lambda handler for sensor data ingestion
    """
    try:
        # Parse request with Decimal for DynamoDB
        body = json.loads(event.get('body', '{}'), parse_float=Decimal)
        
        # Extract user_id from path (preferred) or body
        path_params = event.get('pathParameters', {})
        user_id = path_params.get('user_id') or body.get('user_id')
        
        sensor_batch = body.get('batch', [])

        # Also support single data point push (not in a 'batch' list) for simple tests
        if not sensor_batch and 'heartRate' in body:
            sensor_batch = [body]

        if not user_id or not sensor_batch:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing user_id or batch'})
            }

        print(f"Received {len(sensor_batch)} samples for user {user_id}")

        # 1. Fast Track: Store Data
        store_sensor_data(user_id, sensor_batch)

        # 2. Trigger Orchestrator (Async)
        # We trigger it every time data comes in to allow the "Brain" to decide if a state change occurred.
        # The Orchestrator will handle the "debouncing" or history analysis.
        invoke_orchestrator(user_id)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data processed',
                'samples_count': len(sensor_batch)
            })
        }

    except Exception as e:
        print(f"Error processing sensor data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def store_sensor_data(user_id, sensor_batch):
    """Store sensor batch in DynamoDB"""
    with health_table.batch_writer() as batch:
        for sensor in sensor_batch:
            # Flatten and add user_id
            # Ensure timestamp exists
            ts = sensor.get('timestamp')
            if not ts:
                ts = int(datetime.now().timestamp() * 1000)
            
            item = {
                'user_id': user_id,
                'timestamp': ts,
                **sensor
            }
            batch.put_item(Item=item)

def invoke_orchestrator(user_id):
    """Invoke agentic loop orchestrator Lambda asynchronously"""
    # Construct function name dynamically based on env
    project = os.environ.get('PROJECT_NAME', 'tamagotchi-health')
    env = os.environ.get('ENV', 'dev')
    function_name = f"{project}-orchestrator-{env}"
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event', # Async - Fire and Forget
            Payload=json.dumps({
                'user_id': user_id,
                'trigger': 'sensor_ingest',
                'timestamp': int(datetime.now().timestamp() * 1000)
            })
        )
    except Exception as e:
        print(f"Failed to invoke orchestrator {function_name}: {e}")