# Execution Plan: Backend & Infrastructure for "Health Companion" MVP

## Objective
Implement the server-side logic and infrastructure to support the "Health Companion" core feature. This includes data ingestion, state determination logic (1-10 states), generative AI dialogue for the companion, and a manual trigger for demonstration purposes.

## Scope
- **Infrastructure (Terraform):** DynamoDB tables, Lambda functions, API Gateway.
- **Backend Logic (Python):** Sensor ingestion, State Machine logic, Bedrock integration.
- **Shared:** Update JSON contracts to support new physiological parameters and state definitions.

## Phase 1: Data Modeling & Contracts [COMPLETED]
1.  [x] **Update `sensor_data.json`**: Added `sleepScore`, `recoveryScore`, and `stressLevel`.
2.  [x] **Update `pet_state.json`**:
    - [x] Added `stateIndex` (integer 1-10).
    - [x] Added `internalReasoning` field.

## Phase 2: Infrastructure Setup (Terraform) [COMPLETED]
1.  [x] **DynamoDB**:
    - [x] `HealthData`: Created `health_data` table (PK: `user_id`, SK: `timestamp`).
    - [x] `PetState`: Existing `user_state` table utilized.
2.  [x] **IAM Roles**: Updated policies for DynamoDB access (both tables) and Bedrock invocation.
3.  [x] **API Gateway**:
    - [x] `POST /sensor-data` (Ingest).
    - [x] `POST /demo/trigger` (New Demo Endpoint).

## Phase 3: Backend Logic Implementation [COMPLETED]
### 3.1 Sensor Ingest Lambda (`ingest/`)
- [x] **Task**: Receives payload, saves to `HealthData`, triggers Orchestrator.
- [x] **Trigger**: Uses `boto3` to async invoke Orchestrator if physiological data is present.

### 3.2 Orchestrator Lambda (`orchestrator/`)
- [x] **Task**: "Brain" logic implemented.
- [x] **Logic (State Machine)**:
    - Implemented `calculate_state_logic`: Maps (Sleep+Recovery)/2 - StressPenalty to 1-10 scale.
- [x] **Logic (GenAI)**:
    - Integrated `bedrock-runtime` with Claude Sonnet.
    - Prompt: German persona, 1st person, empathic.
- [x] **Persistence**: Updates `user_state` table.

### 3.3 Demo Trigger Lambda (`demo/`)
- [x] **Task**: Implemented `demo/trigger.py`.
- [x] **Action**: Accepts `force_state` and `custom_message`, bypasses logic, invokes Orchestrator with overrides.

## Phase 4: Deployment & Verification [PENDING]
1.  [ ] **Deploy**: Run `terraform apply` to provision resources.
2.  [ ] **Test Ingest**: `curl -X POST https://.../sensor-data -d '{"user_id": "test", "batch": [{"heartRate": 70, "sleepScore": 80, "recoveryScore": 90}]}'`
3.  [ ] **Verify DB**: Check `health_data` for record and `user_state` for calculated state (should be high/happy).
4.  [ ] **Test Demo**: `curl -X POST https://.../demo/trigger -d '{"user_id": "demo", "force_state": 2}'`
5.  [ ] **Verify Demo**: Check `user_state` for State 2 (Sick/Exhausted).