# Architecture Documentation

AI Tamagotchi Health Companion - System Architecture

## Overview

A distributed edge-cloud system combining HarmonyOS wearables, phone bridge, and AWS AI backend to create an autonomous health coach disguised as a virtual pet.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EDGE LAYER (Watch 5)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Sensor Layer │  │ Pet UI/State │  │ Sport Face   │             │
│  │  - HR @50Hz  │──│   Machine    │──│  (Ambient/   │             │
│  │  - Accel/Gyro│  │  - Mood FSM  │  │   Active)    │             │
│  │  - GPS/Baro  │  │  - Animation │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                           │ DSoftBus                                │
└───────────────────────────┼─────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BRIDGE LAYER (Phone)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ DSoftBus     │  │ Data         │  │ Auth         │             │
│  │ Connector    │──│ Aggregator   │──│ Gateway      │             │
│  │              │  │ (Batching)   │  │ (Cognito)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                           │ HTTPS/WSS                               │
└───────────────────────────┼─────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CLOUD LAYER (AWS)                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Gateway (REST + WebSocket)            │  │
│  └────────┬─────────────────────────────────────────────────────┘  │
│           │                                                          │
│     ┌─────▼─────┐         ┌──────────────┐      ┌──────────────┐  │
│     │  Lambda   │────────▶│   Bedrock    │      │  SageMaker   │  │
│     │ Functions │         │   Agents     │      │   Models     │  │
│     │           │◀────────│ (LLM Brain)  │      │ (Predictive) │  │
│     └─────┬─────┘         └──────────────┘      └──────────────┘  │
│           │                                                          │
│     ┌─────▼─────────────────────────────────────────────────────┐  │
│     │             DynamoDB (User State + History)               │  │
│     └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Sensor Data Pipeline (Upstream)

```
1. Watch collects HR @ 50Hz
   └─> SensorService.arkts

2. Data sent via DSoftBus to Phone
   └─> WatchConnector.kt

3. Phone batches 50 samples (1 second)
   └─> DataAggregator.kt

4. Batch uploaded to Lambda
   └─> sensor_ingest.py

5. Stored in DynamoDB + Triggers Agentic Loop
   └─> agentic_loop.py
```

### Agentic Loop (Bidirectional)

```
PERCEPTION
├─> Gather sensor data, health history, calendar
└─> Lambda: gather_context()

REASONING (LLM)
├─> Bedrock Agent analyzes situation
│   Input: "HRV declining, sleep 5hrs, scheduled HIIT"
└─> Output: {"reasoning": "...", "actions": [...]}

PLANNING
├─> Parse LLM response into action plan
└─> Lambda: parse_action_plan()

ACTION (Autonomous)
├─> Modify calendar (downgrade workout)
├─> Update pet state (mood: Concerned)
└─> Send WebSocket to Phone → DSoftBus → Watch
```

### Pet State Update (Downstream)

```
1. Lambda updates DynamoDB pet state
   └─> update_pet_state.py

2. WebSocket message to Phone
   └─> CloudClient.kt

3. DSoftBus publish to Watch
   └─> WatchConnector.kt

4. Watch updates UI + Haptic
   └─> Index.arkts + PetStateMachine.arkts
```

## Component Responsibilities

### Watch (Edge)
- **Critical**: Immediate responses (HR > 180 → haptic warning)
- **UI**: Pet rendering, Sport Face modes
- **Sensors**: Raw data collection, no heavy processing
- **Offline**: Basic pet mood logic when disconnected

### Phone (Bridge)
- **Data Aggregation**: Reduce 50Hz stream to manageable chunks
- **Authentication**: Secure AWS credential management
- **Offline Queue**: Store sensor data when network unavailable
- **Local ML** (Optional): Run lightweight models to reduce cloud latency

### Cloud (Brain)
- **Bedrock Agents**: Qualitative reasoning (LLM-based)
- **SageMaker**: Quantitative predictions (ML models)
- **Lambda**: Orchestration and API endpoints
- **DynamoDB**: User state persistence

## Technology Decisions

### Why Distributed Architecture?
- **Watch constraints**: Limited compute, battery life
- **Phone advantages**: More power, persistent connection
- **Cloud benefits**: Scalable AI, state sync across devices

### Why Bedrock + SageMaker?
- **Bedrock**: Natural language reasoning for complex health decisions
- **SageMaker**: Specialized models for HRV, stress classification
- **Hybrid approach**: LLM creativity + ML precision

### Why DSoftBus?
- **Native HarmonyOS**: Official Huawei protocol for Super Devices
- **Low latency**: Direct watch-phone communication
- **Unified abstraction**: Treat watch + phone as single system

## Security Architecture

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│  Watch  │────────▶│  Phone  │────────▶│   AWS   │
└─────────┘         └─────────┘         └─────────┘
  DSoftBus            HTTPS/WSS          IAM
  (Encrypted)         (TLS 1.3)          (Cognito)
```

- **Watch-Phone**: DSoftBus encryption (paired devices)
- **Phone-Cloud**: HTTPS, AWS Cognito authentication
- **Data Storage**: DynamoDB encryption at rest
- **GDPR**: eu-central-1 region, user data deletion support

## Scalability

### Horizontal Scaling
- **Lambda**: Auto-scales to 1000s concurrent users
- **DynamoDB**: On-demand capacity (no provisioning)
- **API Gateway**: Handles 10,000 req/s per account

### Cost Optimization
- **Lambda ARM**: 20% cost reduction (Graviton2)
- **Bedrock Haiku**: Use cheaper model for non-critical reasoning
- **SageMaker Serverless**: Only pay when inference runs
- **DynamoDB On-Demand**: No idle capacity costs

## Failure Modes & Resilience

| Failure Scenario | System Behavior |
|------------------|----------------|
| **Phone offline** | Watch continues basic pet mood logic, queues data |
| **Cloud unreachable** | Phone queues sensor batches, syncs when back online |
| **Lambda timeout** | API Gateway retries, DLQ for failed events |
| **Bedrock rate limit** | Fallback to simpler rule-based actions |
| **SageMaker endpoint down** | Use cached predictions, alert monitoring |

## Development Workflow

### Local Development
```bash
# Watch: DevEco Studio with physical Watch 5
# Phone: Android Studio with physical phone
# Cloud: AWS SAM local testing

sam local start-api --port 3000
# Phone points to localhost:3000 for testing
```

### CI/CD Pipeline (Future)
```
1. Git push → GitHub Actions
2. Watch: Build .hap, deploy to test Watch
3. Phone: Build .apk, deploy to test phone
4. Cloud: sam build && sam deploy --guided
5. Integration tests across all layers
```

## Monitoring & Observability

### Metrics to Track
- **Watch**: Battery drain, sensor sampling rate, UI frame rate
- **Phone**: DSoftBus connection reliability, batch upload latency
- **Cloud**: Lambda cold starts, Bedrock latency, DynamoDB throttles

### Logging Strategy
```
Watch  → System logs (HarmonyOS Logger)
Phone  → Logcat (Android) or system logs
Cloud  → CloudWatch Logs (structured JSON)
```

### Alerts
- HR > 200 for 1 min → Emergency alert to user
- Lambda error rate > 5% → Notify on-call engineer
- DynamoDB write throttles → Auto-scale capacity

## Future Enhancements

### Phase 2 (Post-Hackathon)
- **Multi-device sync**: iPad/desktop web app
- **Social features**: Pet interactions between users
- **Advanced ML**: Real-time form correction using gyroscope
- **Voice integration**: Hands-free coaching during runs

### Phase 3 (Production)
- **FDA compliance**: Medical device certification for chronic conditions
- **Third-party integrations**: Strava, Apple Health, Google Fit
- **White-label**: Allow hospitals to customize pet/branding
- **Subscription model**: Freemium with premium features

## References

- [HarmonyOS Documentation](https://developer.huawei.com/consumer/en/harmonyos)
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [SageMaker Deployment](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html)
- [DSoftBus Protocol](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/distributed-softbus-V5)
