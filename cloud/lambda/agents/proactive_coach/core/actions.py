import os
import boto3
import json

lambda_client = boto3.client('lambda')

def invoke_avatar_generator(user_id):
    project = os.environ.get('PROJECT_NAME', 'tamagotchi-health')
    env = os.environ.get('ENV', 'dev')
    function_name = f"{project}-avatar-generator-{env}"
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps({'user_id': user_id})
        )
    except Exception as e:
        print(f"Failed to invoke avatar generator ({function_name}): {e}")
