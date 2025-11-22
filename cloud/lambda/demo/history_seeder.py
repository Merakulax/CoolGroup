import argparse
import boto3
import time
import random
import math
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Default Table Name (can be overridden by env var)
TABLE_NAME = os.environ.get('HEALTH_TABLE', 'health_data')
DEFAULT_REGION = os.environ.get('AWS_REGION', 'eu-central-1')

class HistorySeeder:
    def __init__(self, table_name, region):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def generate_datapoint(self, user_id, timestamp, profile, progress_ratio):
        """
        Generates a single data point based on the profile and progress through the timeline.
        progress_ratio: 0.0 (start of history) -> 1.0 (now)
        """
        
        # Base Metrics
        base_hr = 70
        base_hrv = 40
        base_sleep = 75
        
        # Profile Modifiers
        if profile == "athlete":
            # Improving: HR goes down, HRV goes up
            hr = base_hr - (10 * progress_ratio) # 70 -> 60
            hrv = base_hrv + (20 * progress_ratio) # 40 -> 60
            sleep = base_sleep + (15 * progress_ratio) # 75 -> 90
            
        elif profile == "burnout":
            # Worsening: HR goes up, HRV goes down drastically
            hr = base_hr + (15 * progress_ratio) # 70 -> 85
            hrv = base_hrv - (20 * progress_ratio) # 40 -> 20
            sleep = base_sleep - (30 * progress_ratio) # 75 -> 45
            
        elif profile == "sick":
            # Sudden deterioration in last 20% of timeline
            if progress_ratio > 0.8:
                hr = base_hr + 20
                hrv = base_hrv - 15
                sleep = base_sleep - 10
            else:
                hr = base_hr
                hrv = base_hrv
                sleep = base_sleep

        else: # "steady"
            hr = base_hr
            hrv = base_hrv
            sleep = base_sleep

        # Add Daily Cycle / Noise
        hour_of_day = datetime.fromtimestamp(timestamp / 1000).hour
        
        # Circadian Rhythm for HR (Lower at night)
        if 0 <= hour_of_day < 6:
            hr -= 10
            hrv += 10
        elif 12 <= hour_of_day < 18:
            hr += 5
            
        # Random Noise
        hr += random.uniform(-3, 3)
        hrv += random.uniform(-5, 5)
        sleep += random.uniform(-5, 5)
        
        # Clamp values
        hr = max(40, min(200, hr))
        hrv = max(10, min(150, hrv))
        sleep = max(0, min(100, sleep))

        return {
            'user_id': user_id,
            'timestamp': int(timestamp),
            'heart_rate': Decimal(str(round(hr, 1))),
            'hrv': Decimal(str(round(hrv, 1))),
            'sleep_score': Decimal(str(round(sleep, 1))),
            'source': 'history_seeder'
        }

    def seed(self, user_id, days, profile):
        print(f"Seeding {days} days of history for user '{user_id}' with profile '{profile}'...")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Generate data points every hour
        current_time = start_time
        batch_items = []
        count = 0
        
        total_hours = days * 24
        hours_processed = 0

        with self.table.batch_writer() as batch:
            while current_time <= end_time:
                ts = current_time.timestamp() * 1000
                
                # Calculate progress (0.0 to 1.0)
                progress = hours_processed / total_hours if total_hours > 0 else 0
                
                item = self.generate_datapoint(user_id, ts, profile, progress)
                
                batch.put_item(Item=item)
                
                current_time += timedelta(hours=1) # 1 hour steps
                count += 1
                hours_processed += 1
                
                if count % 100 == 0:
                    print(f"  Generated {count} points...")

        print(f"Done! Wrote {count} items to {self.table.name}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed DynamoDB with mock health history")
    parser.add_argument("--user_id", type=str, default="demo_user", help="User ID")
    parser.add_argument("--days", type=int, default=7, help="Number of days to generate")
    parser.add_argument("--profile", type=str, choices=["athlete", "burnout", "sick", "steady"], default="steady", help="Health profile curve")
    parser.add_argument("--table", type=str, default=TABLE_NAME, help="DynamoDB Table Name")
    parser.add_argument("--region", type=str, default=DEFAULT_REGION, help="AWS Region")

    args = parser.parse_args()
    
    seeder = HistorySeeder(args.table, args.region)
    seeder.seed(args.user_id, args.days, args.profile)
