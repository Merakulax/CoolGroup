# Huawei Health Service API Summary for AI Tamagotchi

This document summarizes the key data types and fields from the Huawei Health Service API relevant to the AI Tamagotchi project.

## Core Biometrics (Vitals)

These data points are crucial for understanding the user's real-time physiological state.

| Data Type | Field | Description | Unit |
|---|---|---|---|
| `HEART_RATE` | `bpm` | Dynamic heart rate | beats/min |
| `HEART_RATE_VARIABILITY` | `heartRateVariabilityRMSSD` | Root Mean Square of Successive Differences between normal heartbeats | ms |
| `BLOOD_OXYGEN_SATURATION` | `spo2` | Blood oxygen saturation | % |
| `RESTING_HEART_RATE` | `restBpm` | Resting heart rate | beats/min |
| `BODY_TEMPERATURE` | `bodyTemperature` | Body temperature | °C |
| `SKIN_TEMPERATURE` | `skinTemperature` | Skin temperature | °C |

## Mental & Cognitive State

This data helps the agent understand the user's mental well-being.

| Data Type | Field | Description | Values |
|---|---|---|---|
| `STRESS` | `stressScore` | User's stress level | 1-99 |
| `EMOTION` | `emotionStatus` | User's emotional state | 1: unpleasant, 2: neutral, 3: pleasant |

## Sleep Analysis

Sleep data is fundamental for the "Spoon Theory" energy budget use case.

| Data Type | Field | Description | Unit |
|---|---|---|---|
| `SLEEP_RECORD` | `sleepScore` | Overall sleep quality score | 0-100 |
| | `duration` | Total sleep duration | seconds |
| | `deepDuration` | Deep sleep duration | seconds |
| | `shallowDuration` | Light sleep duration | seconds |
| | `dreamDuration` | REM sleep duration | seconds |
| | `wakeCount` | Number of times woken up | count |
| | `deepSleepContinuity`| Deep sleep continuity score | 0-100 |
| `SLEEP_NAP_RECORD` | `noonDuration` | Duration of naps | seconds |

## Physical Activity & Environment

This data provides context about the user's physical exertion and location.

| Data Type | Field | Description | Unit |
|---|---|---|---|
| `DAILY_ACTIVITIES` | `step` | Daily step count | steps |
| | `calorie` | Calories burned | cal |
| | `distance` | Distance walked/run | meters |
| | `isIntensity` | Medium/high-intensity activity | 0/1 |
| `LOCATION` | `latitude`, `longitude`| GPS coordinates | degrees |
| `RunningForm` | `groundImpactAcceleration`| Landing impact force | g |
| | `verticalOscillation` | Up-and-down motion while running | cm |
| | `groundContactTime` | Time foot spends on the ground | ms |

## Next Steps (Exec Plan)

1.  **Implement Data Listeners**: Create services on the watch to listen for updates to these specific `healthStore.DataType`s.
2.  **Prioritize Data**:
    *   **Phase 1 (Core Vitals)**: `HEART_RATE`, `STRESS`, `SLEEP_RECORD`. These are essential for the pet's basic mood and energy.
    *   **Phase 2 (Activity)**: `DAILY_ACTIVITIES`, `RunningForm`. Link pet animation and coaching to user movement.
    *   **Phase 3 (Refinement)**: `HEART_RATE_VARIABILITY`, `EMOTION`. Use for more nuanced pet reactions and proactive interventions.
3.  **Data Aggregation**: Implement logic on the phone to aggregate and summarize high-frequency data (like `HEART_RATE`) before sending it to the cloud.
4.  **Cloud Ingestion**: Create a `sensor_ingest` Lambda function to receive and store this data in DynamoDB, tied to a user profile.
5.  **Agent Reasoning**: Update the Bedrock Agent to incorporate these new data streams into its reasoning process for proactive interventions.
