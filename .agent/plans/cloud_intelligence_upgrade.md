# Cloud Intelligence Upgrade: Personalization & Prediction

## Context
The current Cloud Orchestrator (`cloud/lambda/orchestrator`) is functional but generic. It treats all users identically and reacts only to immediate sensor data. This plan aims to implement **Personalization (Persona Injection)** and **Predictive Context** to align with the "AI Tamagotchi" research goals.

## Goals
1.  **Personalization (Part A)**: Transform `proactive_coach.py` to adapt its tone and advice based on a user's `motivation_profile` (e.g., "Drill Sergeant" vs. "Empathetic Friend").
2.  **Prediction (Part B)**: Empower `state_reactor.py` with a new `predictions.py` module that provides trend analysis (e.g., "HRV is declining over 3 days") to the LLM, enabling proactive warnings.

## Architecture Changes

### 1. Data Model Updates (`core/database.py`)
*   **Current**: Returns raw user dict.
*   **Change**: Enhance `get_all_users()` and `get_user_profile()` to return (or mock) motivation fields:
    *   `motivation_style`: `["STRICT", "ENCOURAGING", "ANALYTICAL"]`
    *   `goals`: `["SLEEP_OPTIMIZATION", "MARATHON_TRAINING", "STRESS_MANAGEMENT"]`

### 2. Personalization Layer (`agents/proactive_coach.py`)
*   **Logic**: Retrieve user profile before invoking LLM.
*   **Prompt Engineering**:
    ```python
    # Dynamic System Prompt
    prompt = f"""You are a {user['motivation_style']} Health Coach.
    The user's primary goal is {user['goals']}.
    Adjust your intervention style accordingly."""
    ```

### 3. Predictive Module (`core/predictions.py`) - **NEW**
*   **Purpose**: A lightweight analysis layer that runs *before* the LLM.
*   **Functions**:
    *   `analyze_trends(user_id, metric='hrv', days=3)`: Returns slope/direction.
    *   `predict_readiness(user_id)`: Simple heuristic combining Sleep + HRV.
*   **Future Proofing**: This module will eventually call SageMaker endpoints. For now, it uses `numpy` or simple math on DynamoDB history.

### 4. Integration (`agents/state_reactor.py`)
*   **Logic**: Call `predictions.analyze_trends()` alongside `database.get_recent_history()`.
*   **Context Injection**: Pass "Predicted Trend: DECLINING" to the `pet_state_analyzer` tool.

## Execution Steps

### Phase 1: Foundation (Data & Predictions)
1.  [ ] Create `cloud/lambda/orchestrator/core/predictions.py` with basic trend algorithms.
2.  [ ] Update `cloud/lambda/orchestrator/core/database.py` to support (mock) user profiles.

### Phase 2: Agent Logic
3.  [ ] Refactor `proactive_coach.py` to inject Persona.
4.  [ ] Refactor `state_reactor.py` to inject Predictive Context.

### Phase 3: Testing
5.  [ ] Update `cloud/lambda/demo/trigger.py` (or create a test script) to simulate different user profiles and historical data trends.
6.  [ ] Verify LLM outputs differ based on profile (A/B testing prompts).
