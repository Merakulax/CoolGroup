import json
import boto3
import os
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

users_table = dynamodb.Table(os.environ.get('USERS_TABLE', 'users'))
bucket_name = os.environ.get('AVATAR_BUCKET', 'avatars')

def handler(event, context):
    print("Event:", json.dumps(event))
    
    route_key = event.get('routeKey')
    
    try:
        if route_key == 'POST /users':
            return create_user(event)
        elif route_key == 'GET /users/{user_id}':
            return get_user(event)
        elif route_key == 'GET /users/{user_id}/avatar/upload-url':
            return get_upload_url(event)
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
        'avatar_url': body.get('avatar_url')
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
        
    # Decimal to float/int conversion might be needed if boto3 doesn't handle it for json dump
    # But simple types usually work.
    
    return {
        "statusCode": 200,
        "body": json.dumps(item, default=str)
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
        
        # Also construct the final public/access URL to store in DB
        # Since bucket is private, they would need another presigned GET URL to view it
        # Or we make the bucket objects public (not recommended usually, but for avatars maybe ok?)
        # For this MVP, let's assume we use the presigned GET or just store the Key.
        # We'll return the upload URL and the Key.
        
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
