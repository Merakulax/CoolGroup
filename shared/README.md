# Shared Module

Shared data models and contracts used across Watch, Phone, and Cloud components.

## Purpose

This module ensures all components communicate using consistent data structures. When making changes:

1. **Version your changes**: Increment version number if breaking compatibility
2. **Update all consumers**: Check Watch, Phone, and Cloud implementations
3. **Document changes**: Add migration notes for breaking changes

## Structure

```
shared/
├── contracts/              # API contracts and interfaces
│   ├── sensor_data.json    # Sensor payload format
│   ├── pet_state.json      # Pet state format
│   └── actions.json        # Action command format
├── models/                 # Language-specific models
│   ├── typescript/         # For Watch (ArkTS)
│   ├── kotlin/             # For Phone (if Kotlin)
│   └── python/             # For Cloud (Lambda)
└── schemas/                # JSON Schema definitions
    └── v1/                 # Version 1 schemas
```

## Contract Versions

### Current Version: v1.0.0

All components must use the same contract version for compatibility.

## Usage

### Watch (ArkTS)
```arkts
import { SensorPayload } from '../../shared/models/typescript/sensor_data';

const payload: SensorPayload = {
  heartRate: 75,
  accelerometer: { x: 0.1, y: 0.2, z: 9.8 },
  timestamp: Date.now()
};
```

### Phone (Kotlin)
```kotlin
import com.coolgroup.shared.models.SensorPayload

val payload = SensorPayload(
  heartRate = 75,
  accelerometer = Triple(0.1, 0.2, 9.8),
  timestamp = System.currentTimeMillis()
)
```

### Cloud (Python)
```python
from shared.models.sensor_data import SensorPayload

payload = SensorPayload(
    heart_rate=75,
    accelerometer={'x': 0.1, 'y': 0.2, 'z': 9.8},
    timestamp=1732234567000
)
```

## Adding New Contracts

1. Define JSON schema in `/schemas/v1/`
2. Generate language-specific models in `/models/`
3. Update this README with usage examples
4. Notify all team members of the new contract

## Breaking Changes

If you need to make breaking changes:

1. Create new version: `/schemas/v2/`
2. Keep v1 for backward compatibility during migration
3. Update component implementations incrementally
4. Document migration path in CHANGELOG.md
