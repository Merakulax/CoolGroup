"""
Sensor Ingestion Lambda
Receives batched sensor data from phone bridge and stores in DynamoDB
"""

import json
import os
from datetime import datetime
# import boto3

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


def handler(event, context):
    """
    Lambda handler for sensor data ingestion

    Expected event body:
    {
        "user_id": "uuid",
        "batch": [
            {
                "heartRate": 75,
                "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8},
                "timestamp": 1732234567000
            },
            ...
        ]
    }
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

        # Store in DynamoDB
        # store_sensor_data(user_id, sensor_batch)

        # Analyze batch for triggers
        analysis = analyze_batch(sensor_batch)

        # Trigger agentic loop if needed
        if should_trigger_agent(analysis):
            print(f"Triggering agentic loop: {analysis['reason']}")
            # invoke_orchestrator(user_id, analysis)

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


def analyze_batch(sensor_batch):
    """Analyze sensor batch for anomalies or triggers"""
    if not sensor_batch:
        return {'anomalies': []}

    # Extract heart rates
    heart_rates = [s.get('heartRate', 0) for s in sensor_batch]
    avg_hr = sum(heart_rates) / len(heart_rates) if heart_rates else 0
    max_hr = max(heart_rates) if heart_rates else 0

    anomalies = []
    if max_hr > 180:
        anomalies.append('heart_rate_critical')
    if avg_hr > 140:
        anomalies.append('elevated_heart_rate')

    return {
        'avg_heart_rate': avg_hr,
        'max_heart_rate': max_hr,
        'anomalies': anomalies,
        'reason': anomalies[0] if anomalies else None
    }


def should_trigger_agent(analysis):
    """Determine if agentic loop should be triggered"""
    return len(analysis.get('anomalies', [])) > 0


def store_sensor_data(user_id, sensor_batch):
    """Store sensor batch in DynamoDB"""
    # TODO: Implement DynamoDB storage
    # table.put_item(Item={
    #     'user_id': user_id,
    #     'timestamp': int(datetime.now().timestamp()),
    #     'sensor_batch': sensor_batch
    # })
    pass


def invoke_orchestrator(user_id, analysis):
    """Invoke agentic loop orchestrator Lambda"""
    # TODO: Implement Lambda invocation
    # lambda_client = boto3.client('lambda')
    # lambda_client.invoke(
    #     FunctionName='AgenticLoopOrchestrator',
    #     InvocationType='Event',
    #     Payload=json.dumps({'user_id': user_id, 'analysis': analysis})
    # )
    pass
