import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('HEALTH_TABLE', 'health_data'))

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def handler(event, context):
    """
    Bedrock Flow Lambda Node: Context Retriever
    Retrieves recent health data from DynamoDB to simulate RAG.
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract inputs from Bedrock Flow event structure
        node_inputs = event.get('node', {}).get('inputs', [])
        inputs_dict = {item['name']: item['value'] for item in node_inputs}
        
        user_id = inputs_dict.get('user_id')
        limit = int(inputs_dict.get('limit', 5))
        
        if not user_id:
            # Fallback if input is simple JSON (testing)
            user_id = event.get('user_id')
        
        if not user_id:
            return {
                'error': 'Missing user_id'
            }

        # Query DynamoDB for recent records (Descending order)
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False, # Descending order (newest first)
            Limit=limit
        )
        
        items = response.get('Items', [])
        
        # Format context string
        context_str = json.dumps(items, cls=DecimalEncoder)
        
        # Return in Bedrock Flow format
        return {
            "context_data": context_str,
            "record_count": len(items)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "error": str(e)
        }
