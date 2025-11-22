# Execution Plan: Multi-Agent Health Analysis

## Status
**Completed** (2025-11-22) - All agents implemented and integrated into Orchestrator.

## Objective
Refactor the monolithic `agentic_loop.py` into a **Multi-Agent System** to improve the accuracy of state detection (specifically distinguishing Stress vs. Exercise) and provide more nuanced coaching.

## The Problem
A single prompt attempting to analyze sleep, heart rate variability, accelerometer data, and location simultaneously often hallucinates or misses subtle correlations (e.g., high HR + zero steps = Stress/Anxiety).

## Proposed Architecture: "The Council of Experts"

We will implement a **Code-based Agent Pattern** within the Orchestrator Lambda.

### 1. The Agents

| Agent | Persona | Input Data | Output |
|-------|---------|------------|--------|
| **Activity Agent** | Biomechanics Expert | Steps, Calories, Distance, Intensity, GPS, **Barometer** (Elevation), **Ambient Light** (Indoor/Outdoor), **Wear Detection**, **Accelerometer/Gyro/Magnetometer** (Raw Motion) | **Context**: `Sedentary`, `Walking`, `Running` (Trail/Track), `Commuting`, `Not Worn` |
| **Vitals Agent** | Cardiologist | HR, HRV, Resting HR, SpO2, Body/Skin Temp, Acute Stress Score | **Physiology**: `Resting`, `Elevated`, `Recovery`, `Panic`, `Fever/Illness` |
| **Wellbeing Agent** | Psychologist | Sleep Stages (Deep/REM/Light), Nap Duration, Wake Count, Emotion Status, Long-term HRV, **Ambient Light** (Circadian) | **Mental State**: `Balanced`, `Burnout Risk`, `Anxious`, `Depressed`, `Well-Rested` |
| **Supervisor** | Health Coach (Synthesizer) | Activity + Vitals + Wellbeing Outputs | **State**: `STRESS`, `EXERCISE`, `CHILL`, `WORK` + **Reasoning** |

### 2. Logic Flow

```mermaid
graph TD
    Data[Health History] --> AA[Activity Agent]
    Data --> VA[Vitals Agent]
    Data --> WA[Wellbeing Agent]
    AA -->|Context: Running + High Elevation| S[Supervisor]
    VA -->|Physiology: High HR + High Temp| S
    WA -->|Mental: Low REM Sleep| S
    
    subgraph "Synthesis Logic"
        S -->|Running + High Elevation + High HR =| R1[Result: EXERCISE (Hill Training)]
        S -->|Sedentary + Dark Light + Low HR =| R2[Result: SLEEP]
        S -->|Not Worn =| R3[Result: UNKNOWN (Off Wrist)]
    end
    
    R1 --> UpdateDB
    R2 --> UpdateDB
    R3 --> UpdateDB
```

## Implementation Steps

### Step 1: Modularization (Completed)
- [x] Create a new package structure in `cloud/lambda/orchestrator/`:
    ```text
    orchestrator/
      ├── agentic_loop.py (Entry point)
      ├── agents/
      │   ├── __init__.py
      │   ├── base_agent.py (Common Bedrock client code)
      │   ├── activity_agent.py
      │   ├── vitals_agent.py
      │   ├── wellbeing_agent.py
      │   └── supervisor_agent.py
      └── requirements.txt
    ```

### Step 2: Agent Prompts (Completed)
- [x] **Activity Agent**: "Analyze movement patterns, **Elevation (Barometer)**, and **Light**. Is the user hiking, running indoors, or commuting? Check **Wear Detection** first."
- [x] **Vitals Agent**: "Analyze cardiovascular and physiological metrics. Look for signs of illness (High Temp + High Resting HR) or acute stress. Ignore movement."
- [x] **Wellbeing Agent**: "Analyze Sleep Architecture (Deep/REM ratios), **Ambient Light exposure**, and Emotion Status. Is the user mentally recovering or accumulating sleep debt/anxiety?"
- [x] **Supervisor**: "Synthesize the reports. If Activity says **'Not Worn'**, ignore Vitals. If Activity says 'Hiking' (High Elevation change) and Vitals says 'High HR', conclude EXERCISE (valid)."

### Step 3: Parallel Execution (Completed)
- [x] Use `concurrent.futures.ThreadPoolExecutor` within the Lambda handler to invoke Activity, Vitals, and Wellbeing agents in parallel.

### Step 4: State Update (Completed)
- [x] The `Supervisor` returns the standard JSON object expected by the rest of the system (`state`, `mood`, `reasoning`).

## Benefits
*   **Accuracy**: Specialized prompts reduce hallucinations.
*   **Extensibility**: Easy to add a "Nutrition Agent" or "Calendar Agent" later without breaking the core logic.
*   **Debuggability**: We can log the "opinion" of each agent separately.
