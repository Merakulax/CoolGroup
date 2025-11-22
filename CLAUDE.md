# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Tamagotchi Health Companion** for HackaTUM 2025 - A virtual pet on Huawei Watch 5 that evolves with user biometrics and acts as an autonomous health coach.

### Dual Challenge Requirements
- **Huawei**: "Wrist Intelligence" - Maximize Watch 5 sensors (X-TAP, HR, GPS, Accelerometer, Gyroscope)
- **Reply**: "Agentic AI" - Autonomous reasoning and proactive intervention (not passive chatbots)

### Core Concept
The pet doesn't just display data - it **acts**: modifies calendars, adjusts workout intensity, initiates breathing sessions without prompting. Uses psychological bonding (Tamagotchi nostalgia) to drive health behavior change.

## Architecture: Distributed Edge-Cloud System

```
Watch 5 (Edge)          Phone (HarmonyOS Bridge)     AWS (Brain)
├─ .ets UI files   ->   ├─ .ts bridge logic      ->  ├─ Bedrock Agent (LLM reasoning)
├─ Sensor @50Hz         ├─ DSoftBus API              ├─ SageMaker (Predictive models)
└─ Haptic feedback      └─ Data aggregation          └─ Lambda orchestration
   ↑                                                      │
   └──────────────────── Pet State Update ────────────────┘
```

### Why This Architecture?
- **Distributed SoftBus**: Treat Watch + Phone as unified "Super Device" - offload heavy AI to phone/cloud
- **Edge-first safety**: Critical feedback (HR limit breach) happens instantly on watch
- **Cloud-based reasoning**: LLM narrative generation and predictions run asynchronously

## Technology Stack

### Watch Development (HarmonyOS 5.1)
- **Language**: ArkTS (TypeScript extension)
- **UI Framework**: ArkUI (Declarative, state-driven - perfect for Pet state machine)
- **IDE**: DevEco Studio (Windows) - **Must use this, NOT Oniro IDE** (no wearable support)
- **Sensors**: `@kit.SensorServiceKit` for local data (NOT Huawei Health Kit OAuth)
- **Target API**: 18 (fallback to 12)

### Phone Bridge (HarmonyOS/TypeScript)
- **Language**: TypeScript (.ts files) - pure logic, no UI
- **Framework**: DSoftBus API (`@kit.DistributedServiceKit`) for Super Device communication
- **Role**: Data aggregation, auth gateway, bridge between watch and cloud
- **NOT Android**: Do NOT use Kotlin (.kt) or Java - this is HarmonyOS native

### Cloud AI Stack (AWS)
- **Bedrock Agents**: "Brain" - orchestrates Agentic Loop (Perception → Reasoning → Planning → Action)
- **SageMaker**: Data science - train models for fatigue prediction, stress classification
- **Lambda**: Routing between SageMaker (quantitative) and Bedrock (qualitative)
- **Region**: eu-central-1 (GDPR compliance)

### Local AI Development
- **Terminal Interface**: Python scripts using Anthropic/Google APIs
- **Environment**: Conda `gemini_cli`

## Critical Technical Constraints

### HarmonyOS-Specific (NOT Android)
- **Permissions**: `ohos.permission.READ_HEALTH_DATA` (OpenHarmony flow)
- **Kernel Abstraction Layer (KAL)**: Allows kernel swaps without app rewrites
- **Hardware Driver Foundation (HDF)**: Standardized sensor API (no vendor-specific code)
- **No Wearable Emulator**: Must test on physical Watch 5

### File Extension Requirements (CRITICAL)

**ALWAYS use these extensions:**
- ✅ `.ets` - ArkTS UI components (ArkUI declarative syntax with `@Component`, `@State`, etc.)
- ✅ `.ts` - Pure TypeScript logic (classes, interfaces, business logic without UI)

**NEVER use these extensions:**
- ❌ `.arkts` - **INVALID** extension that breaks DevEco Studio syntax highlighting and build
- ❌ `.kt` - Kotlin files are for Android, NOT HarmonyOS (this is NOT an Android project)
- ❌ `.java` - Java is for Android, NOT HarmonyOS

**Why this matters:**
1. **DevEco Studio** only recognizes `.ets` and `.ts` for HarmonyOS projects
2. Using wrong extensions causes:
   - No syntax highlighting
   - Project sync failures
   - Build errors
3. **DSoftBus** is a HarmonyOS API - phone bridge must use TypeScript (.ts), not Kotlin

**File organization:**
```
watch/src/main/
├─ pages/Index.ets          # Main watch face (UI component)
├─ services/SensorService.ets   # May have UI callbacks
└─ services/PetStateMachine.ets  # State machine logic

phone/src/bridge/
├─ WatchConnector.ts        # DSoftBus communication (pure logic)
└─ DataAggregator.ts        # Sensor batching (pure logic)

shared/models/
└─ types.ts                 # Shared interfaces/types
```

### ArkUI State Machine Pattern
```arkts
@State petMood: string = 'Happy'
@State heartRate: number = 70

// Declarative binding - UI auto-updates
if (petMood === 'Happy') { SmileAnimation() }
if (heartRate > 180) { petMood = 'Concerned' }
```

### Sensor Fusion for Data Science
- **Raw R-R intervals** (not pre-calc stress scores) → Custom HRV models
- **HR + Accelerometer correlation**: Distinguish exercise stress vs anxiety stress
- **GPS + Barometer**: Environment-reactive pet behavior (climbing animation on hills)

### Sport Face Modes
1. **Ambient (Low Power)**: Static pet, 1-min data updates
2. **Active (High Power)**: Full animation, continuous sensor sampling during workouts

## Key Use Cases

### 1. Recovery Management (Chronic Conditions)
- **Spoon Theory**: Daily energy budget based on HRV/sleep
- **Agentic Action**: "You've used 80% energy. I'm canceling your evening plans to prevent flare-up."

### 2. Athletic Training
- **Form Mirroring**: Pet mimics bad running form detected by gyroscope → user self-corrects
- **Voice Coaching**: "You're fading. Push 3 more minutes, then walk." (hands-free during runs)

### 3. Proactive Intervention
- **Example**: Low sleep score + scheduled HIIT → Agent downgrades to Zone 2 recovery run, updates calendar

## Development Commands

### Windows Setup
```bash
# Activate AI environment
conda activate gemini_cli

# Terminal AI query (when implemented)
python tools/ai_helper.py "How do I access Watch 5 heart rate in ArkTS?"
```

### Watch Deployment
1. Connect Watch 5 via USB
2. Enable debugging: Settings → About → Tap Build 7x → Developer Options → USB Debugging
3. Run/Debug in DevEco Studio

## Hackathon Execution Phases (48 hours)

| Phase | Hours | Objective | Key Deliverables |
|-------|-------|-----------|------------------|
| **Foundation** | 0-6 | Environment & Architecture | DevEco Studio, AWS Bedrock Agent, JSON schema |
| **Body** | 6-18 | UI & Sensors | Pet animations, HR→PetSpeed binding, Sport Face |
| **Brain** | 18-30 | AI Integration | SageMaker model, Bedrock Agent, DSoftBus bridge |
| **Agent** | 30-40 | Autonomy | Agentic Loop (proactive actions without prompts) |
| **Polish** | 40-48 | Demo & Pitch | Video demo, architecture slides |

## Key Files
- `tools/context.md` - Original project brief and detailed requirements
- `SETUP.md` - Windows environment setup guide (to be created)
- `ARCHITECTURE.md` - Detailed system design (to be created)

Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.