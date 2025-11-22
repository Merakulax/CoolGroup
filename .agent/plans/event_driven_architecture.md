# Execution Plan: Event-Driven AI Architecture

## Objective
Transform the backend into an asynchronous, event-driven system where high-frequency sensor data is ingested cheaply, analyzed for trends using AI, and only triggers expensive visual updates (Avatar Generation) when significant state changes occur.

## Architecture Overview

```mermaid
graph TD
    Watch -->|1. POST /sensor-data| API[API Gateway]
    API --> L1[**Ingest Lambda**]
    
    subgraph "Fast Track (Sync)"
        L1 -->|Save Batch| DB1[(Health Data DB)]
        L1 -.->|Trigger Async| L2[**Orchestrator Lambda**]
        L1 -->|200 OK| Watch
    end
    
    subgraph "Smart Track (Async)"
        L2 -->|Query History (15m)| DB1
        L2 -->|Analyze Trend| AI[**Bedrock (Claude)**]
        AI -->|Result: State + Reason| L2
        L2 -->|Compare vs Last State| DB2[(User State DB)]
        L2 -.->|IF CHANGED| L3[**Avatar Generator**]
    end
```

## Phase 1: Ingest Optimization (Fast Track)
**Goal:** Minimize latency for the watch and decouple analysis.
1.  **Modify `sensor_ingest.py`**:
    *   Ensure it strictly saves data and returns `200 OK`.
    *   Ensure `invoke_orchestrator` is always called `Event` (Async).
    *   Pass minimal context (User ID) to Orchestrator; let Orchestrator fetch what it needs to avoid payload size limits or consistency issues.

## Phase 2: Intelligent Orchestration (Smart Track)
**Goal:** Implement the "Brain" that decides *when* to act.
1.  **Modify `agentic_loop.py`**:
    *   **History Query:** Implement `get_recent_health_data(user_id, limit=20)` to fetch context from DynamoDB.
    *   **Trend Analysis Prompt:** Update the Bedrock prompt to analyze *trends* (e.g., "HR is rising while Steps are 0 -> Stress" vs "HR is rising while Steps > 100 -> Exercise").
    *   **State Diffing:**
        *   Fetch `current_state` from `UserState` table.
        *   Compare calculated `new_state` vs `current_state`.
        *   Only proceed if `new_state != current_state` OR `force_refresh` is True.
    *   **Invoke Avatar Generator:**
        *   If state changed, invoke `avatar_generator` Lambda asynchronously.
        *   Pass the `new_state` and `reasoning` to the generator.

## Phase 3: Visual Update
**Goal:** Generate the visual representation of the new state.
1.  **Update `generator.py`**:
    *   Ensure it accepts `state` and `reasoning` from the event payload (instead of just recalculating from raw data, though it can double-check).
    *   (Done) It already generates images using Gemini.

## Implementation Steps

### Step 1: Update Ingest Lambda
- [ ] Edit `cloud/lambda/ingest/sensor_ingest.py`.
- [ ] Remove heavy local analysis logic if present.
- [ ] Ensure Async invocation of Orchestrator.

### Step 2: Update Orchestrator Lambda
- [ ] Edit `cloud/lambda/orchestrator/agentic_loop.py`.
- [ ] Add `query_health_history` function.
- [ ] Integrate Bedrock for *Trend Analysis*.
- [ ] Implement "State Diff" logic.
- [ ] **Implement State Hash/Timestamp generation:** Ensure `timestamp` or `hash` is saved to `UserState` DB on every update.
- [ ] Add logic to invoke `avatar_generator`.

### Step 3: Update Generator Lambda (Async Writer)
- [ ] Edit `cloud/lambda/avatar/generator.py`.
- [ ] **CRITICAL:** Remove "Return HTTP Response" logic (it is now an async worker).
- [ ] Add logic to **UPDATE** the `UserState` DynamoDB table with the new `image_url` and `last_generated_timestamp`.
- [ ] Ensure it accepts direct invocation payload (`user_id`).

### Step 4: State Sync Endpoint (Fast Reader)
- [ ] Edit `cloud/lambda/user/manager.py`.
- [ ] Add handler for `GET /avatar/current-state/{user_id}`.
- [ ] Logic: Query `UserState` table -> Return `{ state_hash, timestamp, image_url, mood }`.
- [ ] Edit `cloud/infrastructure/terraform/api_gateway.tf`.
- [ ] **Repoint Route:** Change target of `GET /avatar/current-state/{user_id}` from `avatar_generator` to `user_manager`.

### Step 5: Deploy & Verify
- [ ] Run `terraform apply`.
- [ ] Test with `POST /sensor-data` (Simulate Watch).
- [ ] Verify logs in CloudWatch (Ingest -> Orchestrator -> Bedrock -> State Update -> Avatar).

## Phase 4: Watch Sync Strategy (Smart Polling)
**Goal:** Efficiently sync state/images to the watch without draining battery.

**Mechanism:** "Piggyback Polling"
1.  **Watch Logic:**
    *   The Watch sends sensor data via `POST /sensor-data`.
    *   Immediately after (or after a short 1-2s delay), it calls `GET /avatar/current-state/{user_id}`.
2.  **Backend Logic:**
    *   The `GET` endpoint returns the current state including a `timestamp` or `state_hash`.
3.  **Efficiency:**
    *   The Watch compares the received `timestamp` with its local last-known timestamp.
    *   **IF changed:** Download the new `image_url` and trigger haptics.
    *   **IF same:** Ignore (saves bandwidth).

**Why:** Piggybacking on the upload cycle uses the radio when it's already active, minimizing tail-energy states.
