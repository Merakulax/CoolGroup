import os
import boto3
import json
from .utils import DecimalEncoder

lambda_client = boto3.client('lambda')

def invoke_avatar_generator(user_id, analysis=None):
    project = os.environ.get('PROJECT_NAME', 'tamagotchi-health')
    env = os.environ.get('ENV', 'dev')
    function_name = f"{project}-avatar-generator-{env}"
    
    payload = {'user_id': user_id}
    if analysis:
        payload['analysis'] = analysis
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps(payload, cls=DecimalEncoder)
        )
    except Exception as e:
        print(f"Failed to invoke avatar generator ({function_name}): {e}")
