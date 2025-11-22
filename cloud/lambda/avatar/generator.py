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
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# Config
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = "global"
API_KEY = os.environ.get("GCP_API_KEY")
USERS_TABLE = os.environ.get("USERS_TABLE")
HEALTH_TABLE = os.environ.get("HEALTH_TABLE")
BUCKET = os.environ.get("AVATAR_BUCKET")

users_table = dynamodb.Table(USERS_TABLE)
health_table = dynamodb.Table(HEALTH_TABLE)


def handler(event, context):
    print("Event:", json.dumps(event))

    user_id = event.get("pathParameters", {}).get("user_id")
    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing user_id"})}

    try:
        # 1. Get Context
        user_profile = get_user_profile(user_id)
        health_data = get_latest_health(user_id)

        # 2. Construct Prompt
        prompt_text = construct_prompt(user_profile, health_data)
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
            "universe_domain": "googleapis.com",
        }

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            CREDENTIALS_INFO
        )
        client = genai.Client(
            vertexai=True, project=PROJECT_ID, location=REGION, credentials=credentials
        )

        contents = [prompt_text]
        avatar_url = user_profile.get("avatar_url")
        if avatar_url:
            try:
                # Download image from S3
                obj = s3.get_object(Bucket=BUCKET, Key=avatar_url.split("/")[-1])
                # image_bytes = obj['Body'].read() # Unused for now
                pass
            except Exception as e:
                print(f"Failed to load init image: {e}")

        # Generate
        model_id = "gemini-2.5-flash-image"

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt_text,
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
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "image_url": url,
                    "prompt": prompt_text,
                    "health_summary": health_data
                })
            }
            
        except Exception as e:
            print(f"Image generation failed: {e}")
            # Fallback is now redundant as the main call uses generate_content, 
            # but we can return the error.
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Image generation failed.",
                    "error": str(e)
                })
            }

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def get_user_profile(user_id):
    resp = users_table.get_item(Key={"user_id": user_id})
    return resp.get("Item", {})


def get_latest_health(user_id):
    # Query health data by timestamp descending
    resp = health_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id),
        ScanIndexForward=False,
        Limit=1,
    )
    items = resp.get("Items", [])
    return items[0] if items else {}


def construct_prompt(user_profile, health_data):
    name = user_profile.get("pet_name", "Pet")
    # Base visual style
    base = f"A cute 3D render of a {name}, digital pet style, vibrant colors, 4k."

    # Health modifiers
    sleep = int(health_data.get("sleepScore", 70))
    stress = int(health_data.get("stressLevel", 30))
    hr = int(health_data.get("heartRate", 70))

    state = []
    if sleep < 50:
        state.append(
            "very tired, sleepy eyes, yawning, wearing pajamas, blue dark lighting"
        )
    elif sleep > 80:
        state.append("energetic, glowing aura, wide awake, bright lighting")

    if stress > 70:
        state.append("nervous, sweating, shaking, chaotic background")
    elif stress < 30:
        state.append("calm, zen, peaceful background, floating")

    if hr > 120:
        state.append("sweating, sporty headband, running motion")

    prompt = f"{base} {', '.join(state)}"
    return prompt
