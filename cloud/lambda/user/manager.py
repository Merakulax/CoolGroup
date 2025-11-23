import json
import boto3
import os
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

users_table = dynamodb.Table(os.environ.get('USERS_TABLE', 'users'))
user_state_table = dynamodb.Table(os.environ.get('USER_STATE_TABLE', 'tamagotchi-health-user-state-dev'))
bucket_name = os.environ.get('AVATAR_BUCKET', 'avatars')

def handler(event, context):
    print("Event:", json.dumps(event))
    
    route_key = event.get('routeKey')
    
    try:
        if route_key == 'POST /api/v1/users':
            return create_user(event)
        elif route_key == 'GET /api/v1/users/{user_id}':
            return get_user(event)
        elif route_key == 'GET /api/v1/users/{user_id}/avatar/upload-url':
            return get_upload_url(event)
        elif route_key == 'GET /api/v1/user/{user_id}/state':
            return get_user_state(event)
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Route not found"})
            }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def create_user(event):
    body = json.loads(event.get('body', '{}'))
    
    # Basic Validation
    required_fields = ['name', 'pet_name']
    for field in required_fields:
        if field not in body:
            return {"statusCode": 400, "body": json.dumps({"error": f"Missing field: {field}"})}
    
    user_id = body.get('user_id', str(uuid.uuid4()))
    
    item = {
        'user_id': user_id,
        'name': body['name'],
        'pet_name': body['pet_name'],
        'age': body.get('age'),
        'health_goals': body.get('health_goals', []),
        'avatar_url': body.get('avatar_url', 'stich')
    }
    
    # Remove None values
    item = {k: v for k, v in item.items() if v is not None}
    
    users_table.put_item(Item=item)
    
    return {
        "statusCode": 201,
        "body": json.dumps(item)
    }

def get_user(event):
    path_params = event.get('pathParameters', {})
    user_id = path_params.get('user_id')
    
    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing user_id"})}
        
    response = users_table.get_item(Key={'user_id': user_id})
    item = response.get('Item')
    
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}
        
    return {
        "statusCode": 200,
        "body": json.dumps(item, default=str)
    }

def get_user_state(event):
    """
    Retrieves the current state of the user, including avatar-related information.
    """
    path_params = event.get('pathParameters', {})
    user_id = path_params.get('user_id')
    
    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing user_id"})}
        
    response = user_state_table.get_item(Key={'user_id': user_id})
    item = response.get('Item')
    
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "State not found"})}
    
    # Construct clean response for Watch
    response_data = {
        "image_url": item.get('image_url'),
        "video_url": item.get('video_url'),
        "timestamp": int(item.get('timestamp', 0)),
        "message": item.get('message')
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(response_data, default=str)
    }

def get_upload_url(event):
    path_params = event.get('pathParameters', {})
    user_id = path_params.get('user_id')
    
    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing user_id"})}
    
    key = f"avatars/{user_id}.jpg"
    
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': key, 'ContentType': 'image/jpeg'},
            ExpiresIn=300
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "upload_url": url,
                "key": key,
                "expires_in": 300
            })
        }
    except ClientError as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps({"error": "Could not generate URL"})}