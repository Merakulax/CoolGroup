import pytest
import time
import uuid
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_activity_detection(api_url, http_session, db_resource, dynamodb_table):
    """
    Verifies that the system correctly guesses the user's activity.
    """
    table = db_resource.Table(dynamodb_table)
    user_id = f"e2e_act_{uuid.uuid4().hex[:8]}"
    
    # 1. Create User
    create_user(api_url, http_session, user_id)
    
    # 2. Ingest "Coding/Stress" Data (Stationary + Elevated HR)
    logger.info("Injecting 'Coding Stress' data...")
    ingest_data(api_url, http_session, user_id, {
        "heartRate": 95,
        "accelerometer": {"x": 0.01, "y": 0.01, "z": 0.99},
        "step_count": 0
    })
    
    # 3. Verify Activity Label
    logger.info("Waiting for Activity Detection...")
    max_retries = 30
    activity = "None"
    
    for i in range(max_retries):
        time.sleep(2)
        try:
            item_resp = table.get_item(Key={'user_id': user_id})
            item = item_resp.get('Item')
            
            if item:
                activity = item.get('activity', 'Unknown')
                logger.info(f"  [Attempt {i+1}] Activity: {activity}")
                
                # We expect something like "Work", "Coding", "Stress", "Sedentary"
                # The LLM might be creative, so we check for keywords.
                # Given the prompt "Work/Gaming" vs "Exercise"
                
                valid_keywords = ["work", "coding", "sitting", "sedentary", "gaming", "desk", "stress"]
                if any(k in activity.lower() for k in valid_keywords):
                    logger.info(f"  ✅ Activity Match! ({activity})")
                    return
        except Exception as e:
            logger.warning(f"  Error polling: {e}")
            
    pytest.fail(f"Failed to detect valid activity for user {user_id}. Last: {activity}")

def create_user(api_url, session, user_id):
    payload = {
        "user_id": user_id,
        "name": f"Test User {user_id}",
        "pet_name": "Bot",
        "goals": ["GENERAL_HEALTH"]
    }
    resp = session.post(f"{api_url}/api/v1/users", json=payload)
    assert resp.status_code in [200, 201]

def ingest_data(api_url, session, user_id, data):
    ts = int(time.time() * 1000)
    payload = {
        "batch": [
            {
                "timestamp": ts,
                **data
            }
        ]
    }
    resp = session.post(f"{api_url}/api/v1/user/{user_id}/data", json=payload)
    assert resp.status_code == 200
