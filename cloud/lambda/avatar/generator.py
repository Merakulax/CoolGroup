import json
import os
import boto3
import base64
import time
import hashlib
from botocore.exceptions import ClientError
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, GenerateVideosConfig, Modality
import google.oauth2.credentials
from google.cloud import storage  # Import GCS client

# Clients
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# Config
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = "us-central1"  # Hardcoded for Gemini 2.5/3 Preview support
API_KEY = os.environ.get("GCP_API_KEY")
USERS_TABLE = os.environ.get("USERS_TABLE")
HEALTH_TABLE = os.environ.get("HEALTH_TABLE")
USER_STATE_TABLE = os.environ.get(
    "USER_STATE_TABLE", "tamagotchi-health-user-state-dev"
)
AVATAR_CACHE_TABLE = os.environ.get(
    "AVATAR_CACHE_TABLE", "tamagotchi-avatar-cache-dev"
)
BUCKET = os.environ.get("AVATAR_BUCKET")  # S3 bucket for images
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")  # GCS bucket for videos and staging

users_table = dynamodb.Table(USERS_TABLE)
health_table = dynamodb.Table(HEALTH_TABLE)
user_state_table = dynamodb.Table(USER_STATE_TABLE)
avatar_cache_table = dynamodb.Table(AVATAR_CACHE_TABLE)

# Hard-coded OAuth2 credentials from user (Global scope to be reused)
CREDENTIALS_INFO = {
    "account": "",
    "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
    "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
    "quota_project_id": "hackatum25mun-1040",
    "refresh_token": "1//03Ck1NMZxjKFfCgYIARAAGAMSNwF-L9Ir-4mPMPDUBM-Ag4x-TWdKpgo4mvY7pVVjZbPro6vW1169ZHJ_V7NxeyCmICVejHElxcQ",
    "type": "authorized_user",
    "universe_domain": "googleapis.com",
}

gcs_client = None
try:
    if storage:
        creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
            CREDENTIALS_INFO
        )
        gcs_client = storage.Client(project=PROJECT_ID, credentials=creds)
        print("GCS Client initialized with credentials.")
except Exception as e:
    print(f"Failed to init GCS client: {e}")


# Helper function to upload bytes to GCS and return GCS URI
def upload_to_gcs(bucket_name, blob_name, data_bytes, content_type):
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data_bytes, content_type=content_type)
    return f"gs://{bucket_name}/{blob_name}"


def generate_cache_key(params):
    """Generate a deterministic SHA256 hash from the state parameters."""
    # Sort keys to ensure consistent ordering
    serialized = json.dumps(params, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_cached_avatar(cache_hash):
    """Retrieve cached avatar URLs from DynamoDB."""
    try:
        resp = avatar_cache_table.get_item(Key={"cache_hash": cache_hash})
        item = resp.get("Item")
        if item:
            print(f"Cache HIT for hash: {cache_hash}")
            return item
        print(f"Cache MISS for hash: {cache_hash}")
        return None
    except Exception as e:
        print(f"Error reading cache: {e}")
        return None


def cache_avatar(cache_hash, image_url, video_url, params):
    """Store generated avatar URLs in DynamoDB."""
    try:
        item = {
            "cache_hash": cache_hash,
            "image_url": image_url,
            "video_url": video_url,
            "state_params": json.dumps(params),
            "created_at": int(time.time()),
        }
        avatar_cache_table.put_item(Item=item)
        print(f"Cached avatar for hash: {cache_hash}")
    except Exception as e:
        print(f"Error writing to cache: {e}")


def handler(event, context):
    print("Event:", json.dumps(event))

    # Support both API Gateway (pathParameters) and Direct Invocation (payload)
    user_id = event.get("user_id")
    if not user_id:
        user_id = event.get("pathParameters", {}).get("user_id")

    if not user_id:
        raise ValueError("Missing user_id")

    try:
        # 1. Get Context
        user_profile = get_user_profile(user_id)
        health_data = get_latest_health(user_id)
        analysis = event.get("analysis", {})

        # CACHE CHECK
        # Extract relevant state parameters for visual uniqueness
        base_selection = user_profile.get("avatar_url", "stich").lower()
        state_enum = analysis.get("state", "NEUTRAL") if analysis else "NEUTRAL"
        mood = analysis.get("mood", "Neutral") if analysis else "Neutral"
        activity = analysis.get("activity", "Unknown") if analysis else "Unknown"

        cache_params = {
            "base_avatar": base_selection,
            "state_enum": state_enum,
            "mood": mood,
            "activity": activity,
            # Note: We deliberately EXCLUDE volatile fields like heartRate, sleepScore, timestamps
            # unless they bucket into a specific visual state handled by construction logic.
            # However, 'construct_prompt' uses specific thresholds (sleep < 50, hr > 130).
            # To be safe, we should include the boolean result of these thresholds in the cache key.
        }

        # Add threshold booleans to cache key to ensure visual consistency
        sleep = int(health_data.get("sleepScore", 70) or 70)
        hr = int(health_data.get("heartRate", 70) or 70)
        is_tired = sleep < 50 and state_enum != "SLEEP"
        is_flushed = hr > 130 and state_enum != "EXERCISE"

        cache_params["is_tired"] = is_tired
        cache_params["is_flushed"] = is_flushed

        cache_hash = generate_cache_key(cache_params)
        cached_item = get_cached_avatar(cache_hash)

        if cached_item:
            image_url = cached_item.get("image_url")
            video_url = cached_item.get("video_url")
            
            # Even on cache hit, we must update the user_state so the frontend gets the event
            if image_url:
                update_user_state_image(user_id, image_url)
            if video_url:
                update_user_state_video(user_id, video_url)

            return {
                "status": "CACHED",
                "image_url": image_url,
                "video_url": video_url,
                "prompt": "Loaded from cache",
            }

        # 2. Construct Prompt (Cache Miss)
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
            "universe_domain": "googleapis.com",
        }

        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            CREDENTIALS_INFO
        )
        client = genai.Client(
            vertexai=True, project=PROJECT_ID, location=REGION, credentials=credentials
        )

        # Fetch Base Image from S3
        s3_key = "base/stich.jpg"  # Default
        if "yoda" in base_selection:
            s3_key = "base/yoda.jpg"
        elif "monster" in base_selection:
            s3_key = "base/monster.png"

        local_base_path = f"/tmp/{base_selection}_base.jpg"

        try:
            s3.download_file(BUCKET, s3_key, local_base_path)
            print(f"Downloaded base image from {s3_key}")
        except Exception as e:
            print(
                f"Failed to download base image {s3_key}: {e}. Using generic generation."
            )
            local_base_path = None

        contents = [prompt_text]

        if local_base_path:
            # Load image for Gemini
            try:
                # Read image bytes
                with open(local_base_path, "rb") as f:
                    image_bytes = f.read()

                # Use inline_data directly to avoid SDK version mismatches with helper methods
                image = types.Part(
                    inline_data=types.Blob(data=image_bytes, mime_type="image/jpeg")
                )
                contents.append(image)
            except Exception as e:
                print(f"Error loading image part: {e}")
                pass

        # Generate using generate_content with IMAGE modality
        model_id = "gemini-2.5-flash-image"

        # Store generated image bytes for video generation
        generated_image_bytes = None
        image_url = None
        gcs_image_uri = None  # New: GCS URI for the generated image

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=[Modality.TEXT, Modality.IMAGE],
                ),
            )

            # Iterate through parts to find the image
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_image_bytes = part.inline_data.data
                    break

            if not generated_image_bytes:
                # Check if there is text explaining why
                text_part = next(
                    (p.text for p in response.candidates[0].content.parts if p.text),
                    "No text returned",
                )
                raise Exception(f"No image generated. Model response: {text_part}")

            # Save Image to S3
            file_name_png = f"generated/{user_id}_{int(time.time())}.png"
            s3.put_object(
                Bucket=BUCKET,
                Key=file_name_png,
                Body=generated_image_bytes,
                ContentType="image/png",
            )

            image_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET, "Key": file_name_png},
                ExpiresIn=3600,
            )

            print(f"Image Generated: {image_url}")

            # 4. Update User State with new Image URL
            update_user_state_image(user_id, image_url)

            # NEW: Upload generated image to GCS for Veo input
            gcs_image_blob_name = f"veo_staging/{user_id}_{int(time.time())}.png"
            gcs_image_uri = upload_to_gcs(
                GCS_BUCKET_NAME, gcs_image_blob_name, generated_image_bytes, "image/png"
            )
            print(f"Staged image to GCS: {gcs_image_uri}")

        except Exception as e:
            print(f"Image generation failed: {e}")
            raise Exception(f"Image generation failed: {e}")

        # 5. Generate Video Loop (Veo)
        video_url = None
        try:
            if gcs_image_uri:
                print("Starting Video Generation with Veo...")

                # Augment prompt for video: Emphasize maintaining visual style, colors, and 3D render while adding natural movement.
                video_prompt = (
                    prompt_text
                    + ", seamless loop, natural movement, breathing, 4k, smooth motion, maintain original colors, preserve style, do not alter visual aesthetics"
                )

                # Use types.Image with GCS URI for first and last frame
                gcs_image_obj = types.Image(
                    gcs_uri=gcs_image_uri, mime_type="image/png"
                )

                # Output GCS URI for the generated video
                output_gcs_video_blob_name = (
                    f"generated_videos/{user_id}_{int(time.time())}.mp4"
                )
                output_gcs_uri = f"gs://{GCS_BUCKET_NAME}/{output_gcs_video_blob_name}"

                operation = client.models.generate_videos(
                    model="veo-3.1-fast-generate-001",
                    prompt=video_prompt,
                    image=gcs_image_obj,  # First frame
                    config=GenerateVideosConfig(
                        last_frame=gcs_image_obj,  # Forces Loop
                        duration_seconds=4,
                        aspect_ratio="9:16",
                        output_gcs_uri=output_gcs_uri,  # Video will be saved here
                    ),
                )

                print("Video generation initiated. Waiting for operation...")

                # Polling loop
                while not operation.done:
                    print("Waiting for video generation...")
                    time.sleep(5)
                    if hasattr(client, "operations") and hasattr(
                        client.operations, "get"
                    ):
                        try:
                            operation = client.operations.get(operation)
                        except:
                            pass

                if operation.result:
                    res = operation.result
                    if hasattr(res, "generated_videos") and res.generated_videos:
                        gcs_uri = res.generated_videos[
                            0
                        ].video.uri  # This is the GCS URI

                        video_url = gcs_uri.replace(
                            "gs://", "https://storage.googleapis.com/"
                        )

                        print(f"Video Generated: {video_url}")

                        # Update User State with Video URL
                        update_user_state_video(user_id, video_url)
                    else:
                        print("No generated_videos in result.")
                        print(res)
                else:
                    print("Operation finished but no result.")

        except Exception as vx:
            print(f"Video generation failed (non-critical): {vx}")
            import traceback
            traceback.print_exc()

        # SAVE TO CACHE
        if image_url or video_url:
            cache_avatar(cache_hash, image_url, video_url, cache_params)

        # Final Response
        result = {
            "status": "GENERATED",
            "image_url": image_url,
            "video_url": video_url,
            "prompt": prompt_text,
        }
        print(json.dumps(result))
        return result

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        raise Exception(f"Unhandled error: {e}")


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


def update_user_state_image(user_id, url):
    """Update the user_state table with the new image URL"""
    try:
        user_state_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set image_url = :u, last_image_generated = :t",
            ExpressionAttributeValues={":u": url, ":t": int(time.time() * 1000)},
        )
        print(f"Updated UserState for {user_id} with image URL.")
    except Exception as e:
        print(f"Failed to update UserState DB: {e}")


def update_user_state_video(user_id, url):
    """Update the user_state table with the new video URL"""
    try:
        user_state_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set video_url = :u, last_video_generated = :t",
            ExpressionAttributeValues={":u": url, ":t": int(time.time() * 1000)},
        )
        print(f"Updated UserState for {user_id} with video URL.")
    except Exception as e:
        print(f"Failed to update UserState DB for video: {e}")


def construct_prompt(user_profile, health_data, analysis=None):
    name = user_profile.get("pet_name", "Pet")

    # Analysis Data
    state_enum = analysis.get("state", "NEUTRAL") if analysis else "NEUTRAL"
    mood = analysis.get("mood", "Neutral") if analysis else "Neutral"
    activity = analysis.get("activity", "Unknown") if analysis else "Unknown"

    # Base visual style
    base = f"Transform this character into a cute 3D render, digital pet style, vibrant colors, 4k, dark background."

    modifiers = []

    # 1. Activity & State Modifiers
    if state_enum == "EXERCISE" or activity in ["Running", "Cycling", "Workout"]:
        modifiers.append("sweating, sporty headband, running motion, dynamic pose")
    elif state_enum == "SLEEP" or activity == "Sleeping" or state_enum == "TIRED":
        modifiers.append("sleeping, zzz particles, wearing pajamas, cozy blanket")
    elif state_enum == "STRESS" or state_enum == "ANXIOUS":
        modifiers.append("nervous expression, shaking, dark clouds, wide eyes")
    elif state_enum == "HAPPY" or state_enum == "NEUTRAL":
        modifiers.append(f"happy, smiling, {mood} expression")
    elif state_enum == "SICKNESS":
        modifiers.append("sick, thermometer in mouth, bed rest, green tint")

    # 2. Health Data Nuances (Fallback or Detail)
    sleep = int(health_data.get("sleepScore", 70) or 70)  # Handle None
    stress_score = int(health_data.get("stressLevel", 30) or 30)
    hr = int(health_data.get("heartRate", 70) or 70)

    if sleep < 50 and state_enum != "SLEEP":
        modifiers.append("tired eyes, yawning")

    if hr > 130 and state_enum != "EXERCISE":
        modifiers.append("flushed face, surprised")

    prompt = f"{base} {', '.join(modifiers)}"

    # Append message to prompt if available to influence video context
    message = analysis.get("message")
    if message:
        prompt += f". The character is saying: '{message}'. No text on screen, no speech bubble, no word balloon."

    return prompt