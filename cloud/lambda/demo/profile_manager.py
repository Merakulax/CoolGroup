import argparse
import boto3
import os
import json

# Defaults
DEFAULT_TABLE = "users"
DEFAULT_REGION = "eu-central-1"

def update_profile(args):
    dynamodb = boto3.resource('dynamodb', region_name=args.region)
    table = dynamodb.Table(args.table)
    
    print(f"Updating Profile for User: {args.user_id}")
    print(f"  - Style: {args.style}")
    print(f"  - Tone: {args.tone}")
    print(f"  - Goals: {args.goals}")
    
    item = {
        'user_id': args.user_id,
        'name': args.name,
        'pet_name': args.pet_name,
        'motivation_style': args.style,
        'preferred_tone': args.tone,
        'goals': args.goals,
        'age': 30, # Default
        'updated_at': str(os.times())
    }
    
    try:
        table.put_item(Item=item)
        print("✅ Profile updated successfully in DynamoDB.")
    except Exception as e:
        print(f"❌ Error updating profile: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage User Profiles for AI Persona Testing")
    
    parser.add_argument("--user_id", type=str, default="demo_user", help="User ID")
    parser.add_argument("--name", type=str, default="Test User", help="User Display Name")
    parser.add_argument("--pet_name", type=str, default="Tamago", help="Pet Name")
    
    parser.add_argument("--style", type=str, default="ENCOURAGING", 
                        choices=["ENCOURAGING", "STRICT", "ANALYTICAL", "CHILL"],
                        help="The coaching style of the agent")
                        
    parser.add_argument("--tone", type=str, default="supportive",
                        choices=["supportive", "direct", "informative", "playful"],
                        help="The tone of voice")
                        
    parser.add_argument("--goals", nargs='+', default=["GENERAL_HEALTH"],
                        help="List of health goals (e.g. WEIGHT_LOSS MARATHON STRESS_REDUCTION)")
                        
    parser.add_argument("--table", type=str, default=DEFAULT_TABLE, help="DynamoDB Users Table")
    parser.add_argument("--region", type=str, default=DEFAULT_REGION, help="AWS Region")

    args = parser.parse_args()
    update_profile(args)
