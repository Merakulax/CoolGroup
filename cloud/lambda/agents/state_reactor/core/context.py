import os
import boto3
import json
from .utils import DecimalEncoder

lambda_client = boto3.client('lambda')
CONTEXT_RETRIEVER_LAMBDA_ARN = os.environ.get('CONTEXT_RETRIEVER_LAMBDA_ARN')

def get_historical_context(user_id):
    if not CONTEXT_RETRIEVER_LAMBDA_ARN:
        print("CONTEXT_RETRIEVER_LAMBDA_ARN is not set.")
        return None
    
    try:
        payload = {'user_id': user_id}
        response = lambda_client.invoke(
            FunctionName=CONTEXT_RETRIEVER_LAMBDA_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        result = json.loads(response['Payload'].read().decode('utf-8'))
        return result
    except Exception as e:
        print(f"Error invoking context retriever: {e}")
        return None
