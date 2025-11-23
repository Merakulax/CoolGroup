import os
import boto3
import json
from .utils import DecimalEncoder

lambda_client = boto3.client('lambda')

def invoke_avatar_generator(user_id, analysis=None):
    function_name = os.environ.get('AVATAR_GENERATOR_FUNCTION_NAME', 'tamagotchi-health-avatar-generator-dev')
    
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
