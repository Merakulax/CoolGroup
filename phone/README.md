# Phone Bridge Module

Phone application that acts as a bridge between Watch 5 and AWS Cloud.

## Overview

This module handles:
- **DSoftBus Integration**: Receive sensor data from Watch 5 via Huawei's Distributed SoftBus
- **Data Aggregation**: Batch and preprocess sensor streams
- **Authentication Gateway**: Manage user auth and AWS credentials
- **Phone Compute**: Run lightweight ML models locally to reduce cloud latency
- **Background Sync**: Queue data when offline, sync when connected

## Architecture Role

```
Watch 5 (Edge)  ──DSoftBus──>  Phone (Bridge)  ──HTTPS──>  AWS Cloud
                                    │
                                    ├─ Auth Gateway
                                    ├─ Data Batching
                                    └─ Local ML (optional)
```

## Project Structure

```
phone/
├── src/
│   ├── bridge/                 # DSoftBus communication
│   │   ├── WatchConnector.kt   # Receive watch data
│   │   ├── DataAggregator.kt   # Batch sensor streams
│   │   └── SyncManager.kt      # Handle offline queue
│   ├── auth/                   # Authentication
│   │   ├── AuthService.kt      # User authentication
│   │   └── CredentialManager.kt # AWS credentials
│   ├── models/                 # Data models
│   │   ├── SensorPayload.kt
│   │   ├── PetStateUpdate.kt
│   │   └── UserProfile.kt
│   └── cloud/                  # Cloud communication
│       ├── CloudClient.kt      # AWS API client
│       └── WebSocketHandler.kt # Real-time updates
├── config/
│   └── dsoftbus_config.json    # DSoftBus configuration
└── build.gradle.kts            # Dependencies (if Kotlin)
```

## Technology Options

**Option 1: Native Android (Kotlin)**
- Best DSoftBus integration (official Huawei SDK)
- Direct access to phone sensors if needed
- Gradle build system

**Option 2: Cross-platform (Flutter/React Native)**
- Single codebase for Android/iOS
- May need native DSoftBus bridge
- Faster UI development

**Decision**: TBD - choose based on team expertise

## Key Responsibilities

### 1. DSoftBus Integration
Receive real-time sensor data from Watch 5 using Huawei's Distributed SoftBus protocol.

```kotlin
// Pseudocode - actual implementation depends on SDK
class WatchConnector {
    fun connectToWatch() {
        DSoftBusManager.subscribe("TamagotchiWatch") { data ->
            val sensorPayload = parseSensorData(data)
            DataAggregator.append(sensorPayload)
        }
    }
}
```

### 2. Data Aggregation
Batch high-frequency sensor data (50Hz) into manageable chunks for cloud upload.

```kotlin
class DataAggregator {
    private val buffer = mutableListOf<SensorReading>()

    fun append(reading: SensorReading) {
        buffer.add(reading)
        if (buffer.size >= BATCH_SIZE || elapsedTime > BATCH_INTERVAL) {
            uploadBatch()
        }
    }
}
```

### 3. Authentication
Manage user login and securely store AWS credentials.

```kotlin
class AuthService {
    fun loginUser(email: String, password: String): UserToken {
        // OAuth flow or custom auth
    }

    fun getAWSCredentials(): AWSCredentials {
        // Cognito or IAM temporary credentials
    }
}
```

### 4. Offline Support
Queue data when network unavailable, sync when back online.

```kotlin
class SyncManager {
    fun queueForSync(data: SensorPayload) {
        if (isOnline) {
            uploadImmediately(data)
        } else {
            saveToLocalDB(data)
        }
    }
}
```

## Data Flow

```
Watch DSoftBus Stream (50Hz)
    ↓
WatchConnector (subscribe)
    ↓
DataAggregator (batch every 1s or 50 samples)
    ↓
SyncManager (queue if offline)
    ↓
CloudClient (HTTPS POST to AWS Lambda)
    ↓
WebSocketHandler (receive pet state updates)
    ↓
DSoftBus Publish (send back to watch)
```

## Getting Started

### Prerequisites
- Android Studio (if Kotlin) or VSCode (if cross-platform)
- Huawei Mobile Services (HMS) SDK
- Physical Android phone (for DSoftBus testing)

### Setup
```bash
cd phone

# If Kotlin/Android
# Open in Android Studio
# Sync Gradle dependencies

# If Flutter
# flutter pub get

# If React Native
# npm install
```

## DSoftBus Configuration

DSoftBus requires device pairing and permission setup:

1. **Pair Watch and Phone**: Huawei Health app or system Bluetooth settings
2. **Grant Permissions**: DSoftBus communication requires location/Bluetooth permissions
3. **Configure Capabilities**: Define device capabilities in `dsoftbus_config.json`

```json
{
  "deviceName": "TamagotchiPhone",
  "deviceType": "Phone",
  "capabilities": ["SensorAggregation", "CloudGateway"]
}
```

## Development Workflow

1. **DSoftBus Testing**: Requires physical Watch 5 + Phone (no emulator support)
2. **Mock Data**: Create mock sensor stream for testing without watch
3. **Cloud Integration**: Use AWS SDK to send data to Lambda endpoints
4. **State Updates**: Handle WebSocket messages for real-time pet state changes

## Environment Variables

Create `.env` file (not committed to git):
```
AWS_REGION=eu-central-1
AWS_API_GATEWAY_URL=https://xxxxx.execute-api.eu-central-1.amazonaws.com
COGNITO_USER_POOL_ID=eu-central-1_xxxxx
COGNITO_CLIENT_ID=xxxxx
```

## Testing

```bash
# Unit tests
./gradlew test  # or equivalent for chosen platform

# Integration tests (requires watch connection)
./gradlew connectedAndroidTest
```

## Resources

- [DSoftBus Documentation](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/distributed-softbus-V5)
- [HMS Core SDK](https://developer.huawei.com/consumer/en/hms)
- [AWS SDK for Android](https://aws.amazon.com/sdk-for-android/)

## Team Member

**Phone Developer** - Focus areas:
- DSoftBus reliability and reconnection logic
- Data batching optimization
- Authentication flow
- Offline queue management
