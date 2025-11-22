# Watch Module - HarmonyOS Application

HarmonyOS 5.1 wearable application for Huawei Watch 5.

## Overview

This module contains the Edge/Watch component that:
- Renders the Tamagotchi pet UI
- Collects sensor data (HR, Accelerometer, Gyroscope, GPS, Barometer)
- Implements Sport Face modes (Ambient/Active)
- Provides haptic feedback
- Handles critical real-time responses (HR limit breach)

## Project Structure

```
watch/
├── entry/                          # Main application entry
│   ├── src/main/
│   │   ├── arkts/
│   │   │   ├── pages/              # UI pages
│   │   │   │   ├── Index.arkts     # Main watch face
│   │   │   │   ├── SportFace.arkts # Sport mode interface
│   │   │   │   └── Settings.arkts  # Configuration
│   │   │   ├── services/           # Business logic
│   │   │   │   ├── SensorService.arkts    # Sensor data collection
│   │   │   │   ├── PetStateMachine.arkts  # Pet behavior logic
│   │   │   │   └── CloudSync.arkts        # Data sync to phone/cloud
│   │   │   ├── models/             # Data models
│   │   │   │   ├── PetState.arkts
│   │   │   │   ├── SensorData.arkts
│   │   │   │   └── HealthMetrics.arkts
│   │   │   └── utils/              # Helper functions
│   │   │       ├── HRVCalculator.arkts
│   │   │       └── AnimationHelpers.arkts
│   │   └── resources/              # Assets
│   │       ├── base/
│   │       │   ├── element/        # Strings, colors
│   │       │   └── media/          # Images, animations
│   │       └── rawfile/            # Raw assets
│   └── build-profile.json5         # Build configuration
├── oh-package.json5                # Dependencies
└── hvigorfile.ts                   # Build scripts
```

## Technology Stack

- **Language**: ArkTS (TypeScript for HarmonyOS)
- **UI Framework**: ArkUI (Declarative, state-driven)
- **Sensors**: `@kit.SensorServiceKit`
- **Target API Level**: 18 (fallback to 12)
- **IDE**: DevEco Studio (Windows only)

## Getting Started

### Prerequisites
1. Install DevEco Studio from Huawei Developer Portal
2. Configure SDK: API 18 (HarmonyOS 5.1)
3. Physical Huawei Watch 5 (no emulator support for wearables)

### Enable Watch Debugging
1. On Watch 5: Settings → About → Tap Build 7x
2. Developer Options → Enable USB Debugging
3. Connect via USB to PC

### Run Application
```bash
# Open in DevEco Studio
# File → Open → Select /watch directory
# Click Run/Debug → Select connected Watch 5
```

## Key Implementation Notes

### Sensor Access Pattern
```arkts
import { sensor } from '@kit.SensorServiceKit';

// Request permission in module.json5
"requestPermissions": [
  { "name": "ohos.permission.READ_HEALTH_DATA" }
]

// Subscribe to heart rate
sensor.on(sensor.SensorId.HEART_RATE, (data) => {
  this.heartRate = data.heartRate;
  this.updatePetMood();
});
```

### State-Driven UI
```arkts
@Entry
@Component
struct WatchFace {
  @State petMood: string = 'Happy';
  @State heartRate: number = 70;

  build() {
    Column() {
      if (this.petMood === 'Happy') {
        PetSmileAnimation()
      } else if (this.petMood === 'Concerned') {
        PetWorryAnimation()
      }
      Text(`HR: ${this.heartRate}`)
    }
  }
}
```

### Sport Face Modes
- **Ambient Mode**: Low power, static UI, 1-min sensor updates
- **Active Mode**: Full animation, continuous sensor sampling (50Hz)

## Data Flow

```
Sensors (50Hz) → SensorService → PetStateMachine → UI Update
                                      ↓
                                 CloudSync → Phone Bridge
```

## Permissions Required

Add to `entry/src/main/module.json5`:
```json
{
  "requestPermissions": [
    { "name": "ohos.permission.READ_HEALTH_DATA" },
    { "name": "ohos.permission.LOCATION" },
    { "name": "ohos.permission.APPROXIMATELY_LOCATION" },
    { "name": "ohos.permission.INTERNET" }
  ]
}
```

## Development Workflow

1. **UI Development**: Work in `/pages` - use ArkUI Previewer for quick iteration
2. **Sensor Testing**: Must use physical device - no emulator support
3. **State Machine**: Implement pet logic in `PetStateMachine.arkts`
4. **Data Contracts**: Import types from `/shared/contracts`

## Testing

```bash
# Run tests (configure in DevEco Studio)
npm test

# Deploy to watch
hvigorw assembleHap
```

## Resources

- [ArkTS Documentation](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/arkts-get-started-V5)
- [SensorServiceKit API](https://developer.huawei.com/consumer/en/doc/harmonyos-references-V5/js-apis-sensor-V5)
- [ArkUI Components](https://developer.huawei.com/consumer/en/doc/harmonyos-references-V5/arkui-ts-components-V5)

## Team Member

**Watch Developer** - Focus areas:
- Pet animation and UI polish
- Sensor data collection reliability
- Sport Face power optimization
- Haptic feedback patterns
