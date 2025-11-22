import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Environment Variables
USER_STATE_TABLE = os.environ.get('DYNAMODB_TABLE', 'user_state')
HEALTH_TABLE = os.environ.get('HEALTH_TABLE', 'health_data')
USERS_TABLE = os.environ.get('USERS_TABLE', 'users')

# Clients
dynamodb = boto3.resource('dynamodb')
user_state_table = dynamodb.Table(USER_STATE_TABLE)
health_table = dynamodb.Table(HEALTH_TABLE)
users_table = dynamodb.Table(USERS_TABLE)

def get_all_users():
    try:
        # In a real scenario, this would come from a user profile table
        # For now, we'll mock some user profiles for demonstration
        all_users = users_table.scan().get('Items', [])
        
        mock_profiles = {
            "user123": {
                "motivation_style": "ENCOURAGING",
                "goals": ["SLEEP_OPTIMIZATION", "STRESS_MANAGEMENT"],
                "preferred_tone": "supportive"
            },
            "user456": {
                "motivation_style": "STRICT",
                "goals": ["MARATHON_TRAINING"],
                "preferred_tone": "direct"
            },
            "user789": {
                "motivation_style": "ANALYTICAL",
                "goals": ["DATA_DRIVEN_IMPROVEMENT"],
                "preferred_tone": "informative"
            }
        }

        # Enrich users with mock profiles
        enriched_users = []
        for user in all_users:
            user_id = user.get('user_id')
            if user_id in mock_profiles:
                user.update(mock_profiles[user_id])
            else:
                # Default profile if not in mock_profiles
                user.update(mock_profiles.get("user123")) # Default to user123's profile
            enriched_users.append(user)
        
        if not enriched_users: # If no real users, create a mock user
            enriched_users.append({"user_id": "user123", **mock_profiles["user123"]})


        return enriched_users
    except Exception as e:
        print(f"DB Scan Error: {e}")
        return []

def get_last_health_reading(user_id):
    try:
        response = health_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False,
            Limit=1
        )
        items = response.get('Items', [])
        if items:
            # Convert Decimal to float/int for JSON serialization logic handled elsewhere or here?
            # The utils.DecimalEncoder handles the serialization, but for logic we might want floats.
            # For now, returning as is (Decimals) is fine if the encoder is used later.
            return items[0]
        return None
    except Exception as e:
        print(f"DB Query Error: {e}")
        return None

def get_recent_history(user_id, limit=5):
    try:
        response = health_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False,
            Limit=limit
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"History Query Error: {e}")
        return []

def get_health_data_range(user_id, start_ts, end_ts):
    """
    Fetches health data for a user within a specific time range.
    
    :param user_id: The user ID.
    :param start_ts: Start timestamp (inclusive) in milliseconds.
    :param end_ts: End timestamp (inclusive) in milliseconds.
    :return: List of health data items.
    """
    try:
        response = health_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('timestamp').between(start_ts, end_ts)
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Range Query Error: {e}")
        return []

def get_last_state(user_id):
    try:
        resp = user_state_table.get_item(Key={'user_id': user_id})
        return resp.get('Item')
    except:
        return None

def update_state_db(user_id, analysis, time_gap):
    item = {
        'user_id': user_id,
        'timestamp': int(datetime.now().timestamp() * 1000),
        'stateEnum': analysis.get('state'),
        'mood': analysis.get('mood', 'Neutral'),
        'reasoning': analysis.get('reasoning', 'No reasoning provided'),
        'last_updated': datetime.now().isoformat()
    }
    try:
        user_state_table.put_item(Item=item)
    except Exception as e:
        print(f"Failed to update DB: {e}")
