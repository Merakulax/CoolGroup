# Team Roles & Responsibilities

CoolGroup - AI Tamagotchi Health Companion

## Team Members (Max 3 Developers Working in Parallel)

### Developer 1: Watch Specialist
**Module**: `/watch`
**Tech Stack**: DevEco Studio, ArkTS, HarmonyOS 5.1

**Primary Responsibilities**:
- [ ] Set up DevEco Studio environment (Windows)
- [ ] Implement sensor data collection (HR, Accelerometer, Gyroscope, GPS, Barometer)
- [ ] Design and implement pet UI animations
- [ ] Create Sport Face modes (Ambient/Active)
- [ ] Implement Pet State Machine (mood transitions)
- [ ] Handle haptic feedback patterns
- [ ] Optimize battery consumption

**Key Files**:
- `watch/entry/src/main/arkts/pages/Index.arkts`
- `watch/entry/src/main/arkts/services/SensorService.arkts`
- `watch/entry/src/main/arkts/services/PetStateMachine.arkts`

**Success Criteria**:
- ✓ Sensor data streams at 50Hz to phone
- ✓ Pet animations respond to heart rate changes
- ✓ Sport Face displays during workouts
- ✓ Haptic feedback on critical events

---

### Developer 2: Phone Bridge Specialist
**Module**: `/phone`
**Tech Stack**: Kotlin (Android) or Cross-platform (Flutter/React Native)

**Primary Responsibilities**:
- [ ] Implement DSoftBus integration with Watch 5
- [ ] Build data aggregation/batching system
- [ ] Create authentication flow (AWS Cognito)
- [ ] Implement cloud communication layer (HTTPS/WebSocket)
- [ ] Handle offline queue management
- [ ] Build local ML inference (optional optimization)

**Key Files**:
- `phone/src/bridge/WatchConnector.kt`
- `phone/src/bridge/DataAggregator.kt`
- `phone/src/auth/AuthService.kt`
- `phone/src/cloud/CloudClient.kt`

**Success Criteria**:
- ✓ DSoftBus reliably receives watch data
- ✓ Sensor batches upload to AWS every 1 second
- ✓ Authentication flow completed
- ✓ Offline queue stores data when disconnected
- ✓ WebSocket receives real-time pet state updates

---

### Developer 3: Cloud/AI Specialist
**Module**: `/cloud`
**Tech Stack**: Python, AWS (Lambda, Bedrock, SageMaker, DynamoDB)

**Primary Responsibilities**:
- [ ] Set up AWS infrastructure (SAM/CloudFormation)
- [ ] Implement Lambda functions (ingest, orchestrator, state manager)
- [ ] Configure Bedrock Agent for agentic reasoning
- [ ] Train and deploy SageMaker models (HRV prediction, stress classification)
- [ ] Design DynamoDB schemas
- [ ] Implement WebSocket API for real-time updates
- [ ] Set up monitoring and logging

**Key Files**:
- `cloud/lambda/ingest/sensor_ingest.py`
- `cloud/lambda/orchestrator/agentic_loop.py`
- `cloud/bedrock/agents/health_coach_agent.json`
- `cloud/sagemaker/models/hrv_predictor/`

**Success Criteria**:
- ✓ Lambda receives and stores sensor batches
- ✓ Bedrock Agent generates autonomous actions
- ✓ SageMaker model predicts fatigue/stress
- ✓ Agentic loop successfully modifies calendar
- ✓ Pet state updates pushed via WebSocket

---

### Developer 4: Integration & QA (Optional/Part-time)
**Module**: All
**Tech Stack**: Cross-functional

**Primary Responsibilities**:
- [ ] Integration testing across all layers
- [ ] Documentation updates
- [ ] Demo video production
- [ ] Pitch deck preparation
- [ ] Bug fixes and polish
- [ ] Code review

**Success Criteria**:
- ✓ End-to-end flow works (sensor → cloud → pet update)
- ✓ Demo video showcases key features
- ✓ All components documented

---

## Collaboration Protocol

### Shared Resources
- **Contracts**: `/shared/contracts` - ALL developers must coordinate changes
- **Models**: `/shared/models` - Import shared types (don't duplicate)
- **Git**: Feature branches, merge to `main` after testing

### Communication Channels
- **Slack/Discord**: Real-time coordination
- **GitHub Issues**: Track bugs and features
- **Stand-ups**: Every 6-8 hours during hackathon

### Merge Strategy
```bash
# Feature branch workflow
git checkout -b feature/watch-sensor-integration
# Make changes
git add .
git commit -m "Implement heart rate sensor integration"
git push origin feature/watch-sensor-integration
# Create PR, get review from another developer
# Merge to main after approval
```

### Integration Points (Critical Coordination)

| Integration | Developer 1 | Developer 2 | Developer 3 |
|-------------|-------------|-------------|-------------|
| **Watch → Phone** | Implements DSoftBus publish | Implements DSoftBus subscribe | - |
| **Phone → Cloud** | - | Implements HTTPS POST | Implements Lambda handler |
| **Cloud → Phone** | - | Implements WebSocket client | Implements WebSocket server |
| **Phone → Watch** | Implements pet state update | Implements DSoftBus publish | - |

### Shared Contract Workflow
1. **Proposal**: Developer proposes contract change in Slack
2. **Review**: All affected developers approve
3. **Update**: Update `/shared/contracts/*.json`
4. **Generate**: Regenerate language-specific models
5. **Commit**: Single commit updating all models
6. **Notify**: Post in Slack that contract is updated

---

## Dependency Graph

```
Watch Development
    ↓
Phone Bridge ──┬──> Cloud Infrastructure
               │         ↓
               └────> Bedrock Agent
                          ↓
                     Integration Testing
```

**Critical Path**: Cloud must be deployed first for Phone to have API endpoints to call.

**Parallel Work**: Watch and Cloud can develop independently using mock data until Phone bridge is ready.

---

## Time Allocation (48-hour Hackathon)

| Phase | Hours | Watch Dev | Phone Dev | Cloud Dev |
|-------|-------|-----------|-----------|-----------|
| **Setup** | 0-6 | DevEco Studio, sensors | DSoftBus integration | AWS SAM, Bedrock |
| **Core Features** | 6-24 | Pet UI, animations | Data batching, auth | Lambda, DynamoDB |
| **AI Integration** | 24-36 | State machine polish | WebSocket client | Bedrock Agent, SageMaker |
| **Integration** | 36-42 | Bug fixes | End-to-end testing | Monitoring, optimization |
| **Demo & Polish** | 42-48 | UI polish, demo video | - | Pitch deck, slides |

---

## Emergency Contacts

- **Watch Issues**: Developer 1 → @watch-specialist
- **Phone Issues**: Developer 2 → @phone-specialist
- **Cloud Issues**: Developer 3 → @cloud-specialist
- **General/Integration**: Developer 4 → @integration-lead

---

## Success Metrics (Team-Wide)

### MVP Definition (Must-Have for Demo)
- [x] Watch collects heart rate data
- [x] Phone receives data via DSoftBus
- [x] Cloud stores data and runs agentic loop
- [x] Bedrock Agent generates at least one autonomous action
- [x] Pet state updates on watch based on cloud decision

### Stretch Goals (Nice-to-Have)
- [ ] SageMaker model deployed (even if simple)
- [ ] Calendar integration (modify workout)
- [ ] Advanced pet animations (more than 2-3 moods)
- [ ] Voice coaching during workouts
- [ ] Real-time form correction (gyroscope)

### Demo Requirements
- [ ] 2-3 minute video showcasing agentic behavior
- [ ] Live demo on physical Watch 5
- [ ] Architecture slides explaining system design
- [ ] GitHub README with setup instructions
