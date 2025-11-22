"""
Sensor Ingestion Lambda
Receives batched sensor data from phone bridge and stores in DynamoDB
"""

import json
import os
import boto3
from datetime import datetime

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
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        sensor_batch = body.get('batch', [])

        if not user_id or not sensor_batch:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing user_id or batch'})
            }

        print(f"Received batch of {len(sensor_batch)} samples for user {user_id}")

        # Store Data (DynamoDB Only)
        store_sensor_data(user_id, sensor_batch)

        # Analyze batch for triggers
        analysis = analyze_batch(sensor_batch)

        # Trigger agentic loop if needed
        if should_trigger_agent(analysis):
            print(f"Triggering agentic loop: {analysis['reason']}")
            invoke_orchestrator(user_id, analysis)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Batch processed successfully',
                'samples_count': len(sensor_batch),
                'analysis': analysis
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
            item = {
                'user_id': user_id,
                'timestamp': sensor.get('timestamp', int(datetime.now().timestamp() * 1000)),
                **sensor
            }
            # Ensure float precision doesn't break DDB (optional, boto3 handles Decimal conversion mostly)
            batch.put_item(Item=item)

def analyze_batch(sensor_batch):
    """Analyze sensor batch for anomalies or triggers"""
    if not sensor_batch:
        return {'anomalies': []}

    # Extract metrics
    heart_rates = [s.get('heartRate', 0) for s in sensor_batch if 'heartRate' in s]
    avg_hr = sum(heart_rates) / len(heart_rates) if heart_rates else 0
    max_hr = max(heart_rates) if heart_rates else 0
    
    # Check for physiological updates
    has_sleep = any('sleepScore' in s for s in sensor_batch)
    has_recovery = any('recoveryScore' in s for s in sensor_batch)
    
    anomalies = []
    if max_hr > 180:
        anomalies.append('heart_rate_critical')
    if avg_hr > 140:
        anomalies.append('elevated_heart_rate')
    if has_sleep:
        anomalies.append('sleep_update')
    if has_recovery:
        anomalies.append('recovery_update')

    return {
        'avg_heart_rate': avg_hr,
        'max_heart_rate': max_hr,
        'anomalies': anomalies,
        'reason': anomalies[0] if anomalies else None
    }


def should_trigger_agent(analysis):
    """Determine if agentic loop should be triggered"""
    return len(analysis.get('anomalies', [])) > 0

def invoke_orchestrator(user_id, analysis):
    """Invoke agentic loop orchestrator Lambda"""
    # Construct function name dynamically or use env var
    project = os.environ.get('PROJECT_NAME', 'CoolGroup') # Fallback
    env = os.environ.get('ENV', 'dev')
    function_name = f"{project}-orchestrator-{env}"
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event', # Async
            Payload=json.dumps({'user_id': user_id, 'analysis': analysis})
        )
    except Exception as e:
        print(f"Failed to invoke orchestrator {function_name}: {e}")
