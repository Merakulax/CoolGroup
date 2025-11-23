import boto3
import json
import sys
import base64

def invoke_lambda():
    client = boto3.client('lambda', region_name='eu-central-1')
    
    payload = {
        "user_id": "test_user_123",
        "analysis": {
            "state": "HAPPY",
            "mood": "Excited",
            "activity": "Dancing",
            "message": "Keep up the good work!"
        }
    }
    
    try:
        print("Invoking Lambda: tamagotchi-health-avatar-generator-dev")
        response = client.invoke(
            FunctionName='tamagotchi-health-avatar-generator-dev',
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json.dumps(payload)
        )
        
        # Print Logs
        if 'LogResult' in response:
            print("\n=== LAMBDA LOGS ===")
            print(base64.b64decode(response['LogResult']).decode('utf-8'))
            print("===================\n")
        
        response_payload = json.loads(response['Payload'].read())
        print("Response:\n", json.dumps(response_payload, indent=2))
        
        if 'errorMessage' in response_payload:
            print("Error in Lambda execution.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error invoking Lambda: {e}")
        sys.exit(1)

if __name__ == "__main__":
    invoke_lambda()
