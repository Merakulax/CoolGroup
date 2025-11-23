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

    def generate_datapoint(self, user_id, timestamp, profile, progress_ratio, daily_sleep_score):
        """
        Generates a single data point based on the profile and progress through the timeline.
        progress_ratio: 0.0 (start of history) -> 1.0 (now)
        """
        
        # Base Metrics
        base_hr = 70
        base_hrv = 40
        
        # Profile Modifiers for HR/HRV trends
        if profile == "athlete":
            # Improving: HR goes down, HRV goes up
            hr = base_hr - (10 * progress_ratio) # 70 -> 60
            hrv = base_hrv + (20 * progress_ratio) # 40 -> 60
            
        elif profile == "burnout":
            # Worsening: HR goes up, HRV goes down drastically
            hr = base_hr + (15 * progress_ratio) # 70 -> 85
            hrv = base_hrv - (20 * progress_ratio) # 40 -> 20
            
        elif profile == "sick":
            # Sudden deterioration in last 20% of timeline
            if progress_ratio > 0.8:
                hr = base_hr + 20
                hrv = base_hrv - 15
            else:
                hr = base_hr
                hrv = base_hrv

        else: # "steady"
            hr = base_hr
            hrv = base_hrv

        # Add Daily Cycle / Noise
        dt = datetime.fromtimestamp(timestamp / 1000)
        hour_of_day = dt.hour
        weekday = dt.weekday() # 0=Mon, 6=Sun
        
        # Circadian Rhythm for HR (Lower at night)
        if 0 <= hour_of_day < 6:
            hr -= 10
            hrv += 10
        elif 12 <= hour_of_day < 18:
            hr += 5
        
        # --- Exercise Logic ---
        # Simulate a workout at 6 PM (18:00)
        is_workout_time = (hour_of_day == 18)
        
        # Probability of working out based on profile
        workout_chance = 0.0
        if profile == "athlete":
            workout_chance = 0.9
        elif profile == "steady":
            workout_chance = 0.5 # Every other day roughly
        elif profile == "burnout":
            workout_chance = 0.1 # Rarely
        
        # We use a deterministic "random" based on the day to keep it consistent for re-runs if needed, 
        # or just use random. But here we want simple randomness.
        # To ensure the *whole hour* is a workout, we decide based on the day, not the specific call (since we call hourly).
        # We can hash the day timestamp to decide if today is a workout day.
        day_seed = int(timestamp / (24 * 3600 * 1000))
        random.seed(day_seed)
        is_workout_day = random.random() < workout_chance
        
        # Reset seed for noise
        random.seed()

        if is_workout_time and is_workout_day:
            # Workout Intensity
            hr += random.uniform(60, 80) # Spike to ~130-150
            hrv -= random.uniform(10, 20) # HRV drops during stress
            hrv = max(5, hrv) # Safety floor

        # Random Noise
        hr += random.uniform(-3, 3)
        hrv += random.uniform(-5, 5)
        
        # Clamp values
        hr = max(40, min(200, hr))
        hrv = max(5, min(150, hrv))
        
        # Sleep score is passed in, no noise added here to keep it constant for the day
        sleep = daily_sleep_score

        return {
            'user_id': user_id,
            'timestamp': int(timestamp),
            'heart_rate': Decimal(str(round(hr, 1))),
            'hrv': Decimal(str(round(hrv, 1))),
            'sleep_score': Decimal(str(round(sleep, 1))),
            'source': 'history_seeder'
        }

    def calculate_daily_sleep(self, profile, progress_ratio):
        """Calculate a sleep score for the day based on profile trend"""
        base_sleep = 75
        
        if profile == "athlete":
            # Improving sleep
            sleep = base_sleep + (15 * progress_ratio)
        elif profile == "burnout":
            # Worsening sleep
            sleep = base_sleep - (30 * progress_ratio)
        elif profile == "sick":
            if progress_ratio > 0.8:
                sleep = base_sleep - 20
            else:
                sleep = base_sleep
        else:
            sleep = base_sleep
            
        # Add day-to-day variance
        sleep += random.uniform(-10, 10)
        return max(0, min(100, sleep))

    def seed(self, user_id, days, profile):
        print(f"Seeding {days} days of history for user '{user_id}' with profile '{profile}'...")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Align start time to the beginning of that hour to be clean
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        
        current_time = start_time
        count = 0
        total_hours = days * 24
        hours_processed = 0
        
        # Initial Sleep Score
        current_sleep_score = self.calculate_daily_sleep(profile, 0)

        with self.table.batch_writer() as batch:
            while current_time <= end_time:
                ts = current_time.timestamp() * 1000
                
                # Calculate progress (0.0 to 1.0)
                progress = hours_processed / total_hours if total_hours > 0 else 0
                
                # Update sleep score at the start of a new day (Midnight)
                if current_time.hour == 0:
                    current_sleep_score = self.calculate_daily_sleep(profile, progress)

                item = self.generate_datapoint(user_id, ts, profile, progress, current_sleep_score)
                
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