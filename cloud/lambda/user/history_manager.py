import boto3
import os
import argparse
from boto3.dynamodb.conditions import Key

DEFAULT_HEALTH_TABLE = os.environ.get('HEALTH_TABLE', 'tamagotchi-health-health-data-dev')
DEFAULT_REGION = os.environ.get('AWS_REGION', 'eu-central-1')

def delete_user_history(user_id: str, table_name: str = DEFAULT_HEALTH_TABLE, region: str = DEFAULT_REGION):
    """
    Deletes all history data for a given user from the health data DynamoDB table.
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)

    print(f"Attempting to delete history for user: {user_id} from table: {table_name}")

    try:
        # Query for items belonging to the user_id
        # Assuming 'user_id' is a partition key or has a GSI on it
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        items_to_delete = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items_to_delete.extend(response['Items'])

        if not items_to_delete:
            print(f"No history data found for user: {user_id}")
            return

        print(f"Found {len(items_to_delete)} items to delete for user: {user_id}")

        # Delete items in batches
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(
                    Key={
                        'user_id': item['user_id'],
                        'timestamp': item['timestamp']
                    }
                )
        print(f"✅ Successfully deleted {len(items_to_delete)} history items for user: {user_id}")

    except Exception as e:
        print(f"❌ Error deleting history for user {user_id}: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete user history from DynamoDB")
    parser.add_argument("--user_id", type=str, required=True, help="The user ID whose history data should be deleted")
    parser.add_argument("--table", type=str, default=DEFAULT_HEALTH_TABLE, help="DynamoDB Health Data Table Name")
    parser.add_argument("--region", type=str, default=DEFAULT_REGION, help="AWS Region")

    args = parser.parse_args()

    delete_user_history(args.user_id, args.table, args.region)
