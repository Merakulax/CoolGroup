import sys
import os
from unittest.mock import MagicMock

# Mock environment variables
os.environ['GCP_PROJECT_ID'] = 'hackatum25mun-1040'
os.environ['USERS_TABLE'] = 'users'
os.environ['HEALTH_TABLE'] = 'health'
os.environ['USER_STATE_TABLE'] = 'user_state'
os.environ['AVATAR_BUCKET'] = 'avatars'

# Mock boto3 before importing generator
mock_boto3 = MagicMock()
mock_dynamodb = MagicMock()
mock_s3 = MagicMock()
mock_table = MagicMock()

mock_boto3.resource.return_value = mock_dynamodb
mock_boto3.client.return_value = mock_s3
mock_dynamodb.Table.return_value = mock_table

# Setup mock returns
mock_table.get_item.return_value = {
    'Item': {
        'pet_name': 'Stitch',
        'avatar_url': 'stich'
    }
}
mock_table.query.return_value = {
    'Items': [{
        'sleepScore': 85,
        'stressLevel': 20,
        'heartRate': 75
    }]
}

# Mock S3 download to create a dummy file if it doesn't exist
def side_effect_download(bucket, key, filename):
    with open(filename, 'wb') as f:
        f.write(b'\xFF\xD8\xFF') # Fake JPEG header
    return None

mock_s3.download_file.side_effect = side_effect_download

# Apply mocks
sys.modules['boto3'] = mock_boto3

# Now import generator
import generator

# Override the global clients in the module just in case
generator.dynamodb = mock_dynamodb
generator.s3 = mock_s3
generator.users_table = mock_table
generator.health_table = mock_table
generator.user_state_table = mock_table

# Test Event
event = {
    "user_id": "test_user_123",
    "analysis": {
        "state": "HAPPY",
        "mood": "Excited",
        "activity": "Dancing"
    }
}

print("Running handler with test event...")
try:
    # We expect this to fail at the API call because we aren't mocking genai, 
    # but we want to see it try to call it.
    # OR if the hardcoded credentials work, it might actually work!
    generator.handler(event, None)
except Exception as e:
    print(f"Execution finished (possibly with error): {e}")
