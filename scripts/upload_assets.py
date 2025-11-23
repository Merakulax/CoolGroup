import boto3
import os

BUCKET_NAME = "tamagotchi-health-avatars-dev"
MAPPING = {
    "stich_base.jpg": "base/stich.jpg",
    "babyYoda_base.jpg": "base/yoda.jpg",
    "blueMonster_base.png": "base/monster.png"
}

s3 = boto3.client('s3', region_name='eu-central-1')

def upload():
    print(f"Uploading assets to {BUCKET_NAME}...")
    for local_file, s3_key in MAPPING.items():
        if os.path.exists(local_file):
            print(f"Uploading {local_file} -> {s3_key}")
            s3.upload_file(local_file, BUCKET_NAME, s3_key)
        else:
            print(f"Skipping {local_file} (not found)")

if __name__ == "__main__":
    upload()
