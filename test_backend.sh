#!/bin/bash

API_URL="https://lnt6x6tek2.execute-api.eu-central-1.amazonaws.com"
USER_ID="test_user_curl_001"
TIMESTAMP=$(date +%s%3N)

echo "--- 1. Creating User ---"
curl -s -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"name\": \"Curl Tester\", \"pet_name\": \"CyberPet\"}" | jq .

echo -e "\n\n--- 2. Sending 'STRESS' Data (High HR, Sedentary) ---"
# Simulate 5 data points to create history
for i in {1..5}; do
    TS=$(($(date +%s%3N) + $i*1000))
    PAYLOAD=$(cat <<EOF
{
  "user_id": "$USER_ID",
  "batch": [
    {
      "timestamp": $TS,
      "deviceId": "watch_emulator",
      "vitals": { "heartRate": 110, "hrvRMSSD": 15, "stressScore": 90, "bodyTemperature": 36.6 },
      "activity": { "stepCount": 0, "speed": 0, "isIntensity": false },
      "status": { "wearDetection": "WORN" },
      "environment": { "ambientLight": 50 }
    }
  ]
}
EOF
)
    curl -s -X POST "$API_URL/sensor-data" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD"
    echo -n "."
done

echo -e "\n\n--- 3. Waiting for Async Processing (30s) ---"
sleep 30

echo -e "\n--- 4. Checking State (Expect STRESS/ANXIETY) ---"
curl -s -X GET "$API_URL/avatar/current-state/$USER_ID" | jq .

echo -e "\n\n--- 5. Sending 'EXERCISE' Data (Running) ---"
for i in {1..5}; do
    TS=$(($(date +%s%3N) + $i*1000))
    PAYLOAD=$(cat <<EOF
{
  "user_id": "$USER_ID",
  "batch": [
    {
      "timestamp": $TS,
      "deviceId": "watch_emulator",
      "vitals": { "heartRate": 150, "hrvRMSSD": 45, "stressScore": 50, "bodyTemperature": 37.5 },
      "activity": { "stepCount": 160, "speed": 3.0, "isIntensity": true },
      "runningForm": { "verticalOscillation": 9.5, "groundContactTime": 240 },
      "status": { "wearDetection": "WORN" },
      "environment": { "ambientLight": 20000, "barometer": 950 }
    }
  ]
}
EOF
)
    curl -s -X POST "$API_URL/sensor-data" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD"
    echo -n "."
done

echo -e "\n\n--- 6. Waiting for Async Processing (30s) ---"
sleep 30

echo -e "\n--- 7. Checking State (Expect EXERCISE) ---"
curl -s -X GET "$API_URL/avatar/current-state/$USER_ID" | jq .
