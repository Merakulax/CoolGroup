# Cloud Demo Tools

This directory contains tools to demonstrate the "Brain" capabilities of the AI Tamagotchi.

## `scenario_injector.py`

A CLI tool to inject mock sensor data patterns and trigger the AI reasoning loop. This allows you to see how the Pet reacts to different biometrics without needing a physical watch or running around.

### Prerequisites
- AWS Credentials configured (`~/.aws/credentials` or via env vars).
- The Cloud Infrastructure must be deployed.

### Usage

```bash
python cloud/lambda/demo/scenario_injector.py --scenario <SCENARIO> [OPTIONS]
```

### Scenarios

| Scenario | Description | Biometrics Injected | Expected AI Reaction |
|----------|-------------|---------------------|----------------------|
| `stress` | High anxiety moment | HR: 120, Motion: None | **Concerned** / Calming Breath |
| `workout` | Intense exercise | HR: 150, Motion: High | **Energetic** / Sport Mode |
| `sleep` | Deep sleep | HR: 55, Motion: None | **Sleepy** / Zzz Animation |
| `normal` | Walking/Resting | HR: 72, Motion: Moderate | **Happy** / Neutral |

### Options

- `--user_id`: Target specific user (default: `demo_user`)
- `--env`: Target environment (default: `dev`)
- `--project`: Project prefix (default: `CoolGroup`)
- `--region`: AWS Region (default: `eu-central-1`)

### Example

Simulate a stress event:
```bash
python cloud/lambda/demo/scenario_injector.py --scenario stress
```

Output:
```
[1/2] Injecting Sensor Data...
      Result: {'message': 'Data processed', 'samples_count': 2}

[2/2] Invoking Orchestrator for Immediate Reaction...
>>> PET STATE CHANGED TO: CONCERNED <<<
Reasoning: User heart rate is elevated (120bpm) but accelerometer data indicates no physical activity. This suggests acute stress or anxiety.
```

## `history_seeder.py`

A tool to populate DynamoDB with long-term historical data. This is essential for testing **Predictive Models** and **Trend Analysis** (e.g., "Is the user's HRV declining over the last week?").

### Usage

```bash
python cloud/lambda/demo/history_seeder.py [OPTIONS]
```

### Profiles

| Profile | Description | Trend Characteristics |
|---------|-------------|-----------------------|
| `athlete` | Improving fitness | HR 📉, HRV 📈, Sleep 📈 |
| `burnout` | Chronic stress accumulation | HR 📈, HRV 📉, Sleep 📉 |
| `sick` | Sudden onset illness | Stable then sudden HR 📈, HRV 📉 (Last 20% of timeline) |
| `steady` | Maintenance mode | Flat trends with daily noise |

### Options

- `--user_id`: Target user (default: `demo_user`)
- `--days`: How many days of history to generate (default: `7`)
- `--profile`: The trend curve to apply (default: `steady`)
- `--table`: DynamoDB table name (default: `health_data`)

## `profile_manager.py`

A tool to configure the User Persona. This changes how the AI "Coach" talks to the user.

### Usage

```bash
python cloud/lambda/demo/profile_manager.py --style STRICT --tone direct --goals MARATHON
```

### Styles
- `ENCOURAGING`: Supportive, gentle.
- `STRICT`: Drill sergeant, demanding.
- `ANALYTICAL`: Data-focused, cold facts.
- `CHILL`: Laid back, low pressure.

## `environment_simulator.py`

Injects complex environmental and situational context beyond just basic heart rate.

### Scenarios

| Scenario | Context | Biometrics |
|----------|---------|------------|
| `hike` | High Altitude (2500m), Sunny | HR 110, SpO2 95% |
| `commute` | High Speed (50km/h), Traffic | HR 85, Stress 60 |
| `fever` | Body Temp 38.5°C | HR 90 (Resting) |

### Usage

```bash
python cloud/lambda/demo/environment_simulator.py --scenario hike
```
