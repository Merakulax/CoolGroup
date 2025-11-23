import json
import os
import boto3
import base64
import time
from botocore.exceptions import ClientError
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, Modality
import google.oauth2.credentials

# Clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Config
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
REGION = "us-central1" # Hardcoded for Gemini 2.5/3 Preview support
API_KEY = os.environ.get('GCP_API_KEY')
USERS_TABLE = os.environ.get('USERS_TABLE')
HEALTH_TABLE = os.environ.get('HEALTH_TABLE')
USER_STATE_TABLE = os.environ.get('USER_STATE_TABLE', 'tamagotchi-health-user-state-dev')
BUCKET = os.environ.get('AVATAR_BUCKET')

users_table = dynamodb.Table(USERS_TABLE)
health_table = dynamodb.Table(HEALTH_TABLE)
user_state_table = dynamodb.Table(USER_STATE_TABLE)

def handler(event, context):
    print("Event:", json.dumps(event))
    
    # Support both API Gateway (pathParameters) and Direct Invocation (payload)
    user_id = event.get('user_id')
    if not user_id:
        user_id = event.get('pathParameters', {}).get('user_id')
        
    if not user_id:
        raise ValueError("Missing user_id")

    try:
        # 1. Get Context
        user_profile = get_user_profile(user_id)
        health_data = get_latest_health(user_id)
        analysis = event.get('analysis', {})
        
        # 2. Construct Prompt
        prompt_text = construct_prompt(user_profile, health_data, analysis)
        print(f"Prompt: {prompt_text}")
        
        # 3. Generate Image
        # Hard-coded OAuth2 credentials from user
        CREDENTIALS_INFO = {
            "account": "",
            "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
            "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
            "quota_project_id": "hackatum25mun-1040",
            "refresh_token": "1//03Ck1NMZxjKFfCgYIARAAGAMSNwF-L9Ir-4mPMPDUBM-Ag4x-TWdKpgo4mvY7pVVjZbPro6vW1169ZHJ_V7NxeyCmICVejHElxcQ",
            "type": "authorized_user",
            "universe_domain": "googleapis.com"
        }
        
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(CREDENTIALS_INFO)
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=REGION, credentials=credentials)

        # Fetch Base Image from S3
        # Use avatar_url as the character identifier (yoda, stich, monster)
        base_selection = user_profile.get('avatar_url', 'stich').lower()
        
        s3_key = "base/stich.jpg" # Default
        if 'yoda' in base_selection:
            s3_key = "base/yoda.jpg"
        elif 'monster' in base_selection:
            s3_key = "base/monster.png"
        
        local_base_path = f"/tmp/{base_selection}_base.jpg"
        
        try:
            s3.download_file(BUCKET, s3_key, local_base_path)
            print(f"Downloaded base image from {s3_key}")
        except Exception as e:
            print(f"Failed to download base image {s3_key}: {e}. Using generic generation.")
            local_base_path = None

        contents = [prompt_text]
        
        if local_base_path:
            # Load image for Gemini
            try:
                from PIL import Image
                image = types.Part.from_image(Image.open(local_base_path))
                contents.append(image)
            except ImportError:
                # Fallback if PIL not available (should be in layer, but just in case)
                with open(local_base_path, "rb") as f:
                    image_bytes = f.read()
                image = types.Part(inline_data=types.Blob(data=image_bytes, mime_type="image/jpeg"))
                contents.append(image)

        # Generate using generate_content with IMAGE modality
        model_id = "gemini-2.5-flash-image" 
        
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=[Modality.TEXT, Modality.IMAGE],
                ),
            )
            
            generated_image_bytes = None
            # Iterate through parts to find the image
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_image_bytes = part.inline_data.data
                    break
            
            if not generated_image_bytes:
                 # Check if there is text explaining why
                 text_part = next((p.text for p in response.candidates[0].content.parts if p.text), "No text returned")
                 raise Exception(f"No image generated. Model response: {text_part}")
            
            # Save to S3
            file_name = f"generated/{user_id}_{int(time.time())}.png"
            s3.put_object(Bucket=BUCKET, Key=file_name, Body=generated_image_bytes, ContentType='image/png')
            
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET, 'Key': file_name},
                ExpiresIn=3600
            )
            
            print(f"Image Generated: {url}")
            
            # 4. Update User State with new Image URL
            update_user_state_image(user_id, url)
            
            print(json.dumps({
                "status": "GENERATED",
                "image_url": url,
                "prompt": prompt_text
            }))
            
        except Exception as e:
            print(f"Image generation failed: {e}")
            raise Exception(f"Image generation failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Unhandled error: {e}")

def get_user_profile(user_id):
    resp = users_table.get_item(Key={'user_id': user_id})
    return resp.get('Item', {})

def get_latest_health(user_id):
    # Query health data by timestamp descending
    resp = health_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id),
        ScanIndexForward=False,
        Limit=1
    )
    items = resp.get('Items', [])
    return items[0] if items else {}

def update_user_state_image(user_id, url):
    """Update the user_state table with the new image URL"""
    try:
        user_state_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="set image_url = :u, last_image_generated = :t",
            ExpressionAttributeValues={
                ':u': url,
                ':t': int(time.time() * 1000)
            }
        )
        print(f"Updated UserState for {user_id} with image URL.")
    except Exception as e:
        print(f"Failed to update UserState DB: {e}")

def construct_prompt(user_profile, health_data, analysis=None):
    name = user_profile.get('pet_name', 'Pet')
    
    # Analysis Data
    state_enum = analysis.get('state', 'NEUTRAL') if analysis else 'NEUTRAL'
    mood = analysis.get('mood', 'Neutral') if analysis else 'Neutral'
    activity = analysis.get('activity', 'Unknown') if analysis else 'Unknown'
    
    # Base visual style
    base = f"Transform this character into a cute 3D render, digital pet style, vibrant colors, 4k."
    
    modifiers = []
    
    # 1. Activity & State Modifiers
    if state_enum == 'EXERCISE' or activity in ['Running', 'Cycling', 'Workout']:
        modifiers.append("sweating, sporty headband, running motion, dynamic pose")
    elif state_enum == 'SLEEP' or activity == 'Sleeping' or state_enum == 'TIRED':
        modifiers.append("sleeping, zzz particles, wearing pajamas, cozy blanket")
    elif state_enum == 'STRESS' or state_enum == 'ANXIOUS':
        modifiers.append("nervous expression, shaking, dark clouds, wide eyes")
    elif state_enum == 'HAPPY' or state_enum == 'NEUTRAL':
        modifiers.append(f"happy, smiling, {mood} expression")
    elif state_enum == 'SICKNESS':
        modifiers.append("sick, thermometer in mouth, bed rest, green tint")
        
    # 2. Health Data Nuances (Fallback or Detail)
    sleep = int(health_data.get('sleepScore', 70) or 70) # Handle None
    stress_score = int(health_data.get('stressLevel', 30) or 30)
    hr = int(health_data.get('heartRate', 70) or 70)
    
    if sleep < 50 and state_enum != 'SLEEP':
        modifiers.append("tired eyes, yawning")
    
    if hr > 130 and state_enum != 'EXERCISE':
        modifiers.append("flushed face, surprised")

    prompt = f"{base} {', '.join(modifiers)}"
    return prompt