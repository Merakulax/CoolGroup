import json
import boto3
import os

lambda_client = boto3.client('lambda')

def handler(event, context):
    print("Demo trigger received", event)
    
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        user_id = body.get('user_id', 'demo_user')
        force_state = body.get('force_state')
        custom_message = body.get('custom_message')
        
        if not force_state:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "force_state is required"})
            }

        # Construct function name
        project = os.environ.get('PROJECT_NAME', 'CoolGroup')
        env = os.environ.get('ENV', 'dev')
        function_name = f"{project}-orchestrator-{env}"
        
        payload = {
            'user_id': user_id,
            'force_state': force_state,
            'custom_message': custom_message
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse', # Wait for result
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Trigger executed",
                "orchestrator_result": result
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
