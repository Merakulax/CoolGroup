# Development Plan: AI Tamagotchi Health Companion

Strategic roadmap for building the project in phases, optimized for the HackaTUM 48-hour timeline.

## Executive Summary

**Goal**: Build a working prototype demonstrating:
1. **Huawei**: Wrist Intelligence (sensor fusion, Sport Face)
2. **Reply**: Agentic AI (autonomous health interventions)

**Strategy**: Build vertically (end-to-end slices) rather than horizontally (complete layers)
- ✅ Each phase delivers a **demoable feature**
- ✅ Parallel workstreams where possible
- ✅ Fail-fast on risky integrations

## Pre-Development: Setup (Before Hackathon Starts)

**Timeline**: Complete BEFORE arriving at HackaTUM

### Critical Path Items
- [ ] DevEco Studio installed and tested (create dummy wearable project)
- [ ] Watch 5 connected and developer mode enabled
- [ ] AWS credentials received from Reply and tested (Bedrock API call)
- [ ] Conda environment working with both Claude and Gemini APIs
- [ ] Terminal AI helper functional
- [ ] Git repository clean and organized

**Validation**: You can deploy "Hello World" to Watch 5 AND make a Bedrock API call.

---

## Phase 1: Foundation (Hours 0-6)

**Objective**: Establish the core architecture skeleton with minimal viable integration.

### 1.1 Watch App Skeleton (2 hours)

**Owner**: Frontend Developer

**Tasks**:
```
1. Create DevEco wearable project: "TamagotchiCompanion"
2. Set up basic ArkUI structure:
   - Index.ets (main entry point)
   - PetView.ets (component for pet display)
   - SensorService.ets (sensor abstraction layer)
3. Implement basic state management:
   @State petMood: string
   @State heartRate: number
4. Test UI Previewer with static pet image
```

**Deliverable**: Static pet displays on watch with hardcoded "Happy" state.

**Code Example**:
```arkts
// PetView.ets
@Component
export struct PetView {
  @State petMood: string = 'Happy'

  build() {
    Column() {
      Image($r('app.media.pet_happy'))
        .width(100)
        .height(100)

      Text(`Mood: ${this.petMood}`)
        .fontSize(14)
    }
  }
}
```

### 1.2 Sensor Integration (2 hours)

**Owner**: Hardware/Sensor Developer

**Tasks**:
```
1. Import @kit.SensorServiceKit
2. Request permissions in module.json5:
   - ohos.permission.READ_HEALTH_DATA
   - ohos.permission.ACTIVITY_MOTION
3. Create HeartRateSensor wrapper:
   - Subscribe to HR updates
   - Emit to state variable
4. Test on physical watch (NOT emulator)
```

**Validation**: Heart rate updates visible as text on watch face every 5 seconds.

**Code Example**:
```arkts
import sensor from '@kit.SensorServiceKit'

export class HeartRateSensor {
  callback: (hr: number) => void

  start(callback: (hr: number) => void) {
    this.callback = callback
    sensor.on(sensor.SensorId.HEART_RATE, (data) => {
      this.callback(data.heartRate)
    })
  }

  stop() {
    sensor.off(sensor.SensorId.HEART_RATE)
  }
}
```

### 1.3 AWS Bedrock Agent Setup (2 hours)

**Owner**: Backend/AI Developer

**Tasks**:
```
1. Create Bedrock Agent in AWS Console:
   - Name: "TamagotchiCoach"
   - Foundation Model: Claude 3.5 Sonnet
   - Instructions: "You are a supportive health coach embodied as a virtual pet..."
2. Define Action Group:
   - set_pet_mood(mood: string)
   - send_notification(message: string)
3. Create API Gateway endpoint to invoke agent
4. Test with curl/Postman
```

**Input Schema**:
```json
{
  "user_id": "test_user",
  "biometrics": {
    "heart_rate": 75,
    "steps": 5000,
    "sleep_minutes": 420
  },
  "context": "User just woke up"
}
```

**Expected Output**:
```json
{
  "pet_state": {
    "mood": "energetic",
    "message": "Good morning! You slept well. Ready for a walk?",
    "animation": "stretch"
  },
  "actions": [
    {
      "type": "notification",
      "content": "Let's aim for 10k steps today!"
    }
  ]
}
```

**Validation**: Can send JSON from Postman → get coherent pet state response.

---

## Phase 2: The Body (Hours 6-18)

**Objective**: Connect sensors to AI and create engaging UI.

### 2.1 Pet Animation System (4 hours)

**Owner**: Frontend Developer

**Tasks**:
```
1. Create pet animation assets:
   - pet_idle.json (Lottie/GIF)
   - pet_happy.json
   - pet_tired.json
   - pet_exercise.json
2. Implement AnimatedPet component with state-driven switching
3. Add transition animations between states
4. Optimize for watch performance (< 30% CPU)
```

**State Machine**:
```
HR < 60 bpm → pet_idle (sleeping/resting)
HR 60-100 → pet_happy (walking)
HR 100-140 → pet_exercise (running)
HR > 140 → pet_tired (panting)
```

### 2.2 Sport Face Layout (3 hours)

**Owner**: Frontend Developer

**Tasks**:
```
1. Detect workout start (HR sustained > 100 for 2 min)
2. Switch to "Active Mode" layout:
   - Pet in top-left (smaller)
   - HR zone indicator (color-coded circles)
   - Current pace/distance
   - Time elapsed
3. Implement voice feedback trigger points
4. Add haptic patterns for zone changes
```

**Haptic Zones**:
```arkts
if (heartRate > userMaxHR * 0.9) {
  vibrator.vibrate({ duration: 200, intensity: 1.0 }) // Sharp alert
}
```

### 2.3 Watch-to-Cloud Bridge (5 hours)

**Owner**: Backend Developer

**Tasks**:
```
1. Create HTTP service on phone (Node.js/Python):
   - Receives data from watch via DSoftBus
   - Aggregates into 1-minute windows
   - Forwards to AWS API Gateway
2. Implement DSoftBus communication on watch:
   - distributedDataManager for state sync
3. Handle offline mode (queue data when no connection)
4. Test latency (target < 2 seconds watch → cloud → watch)
```

**Architecture**:
```
Watch (ArkTS)           Phone (Bridge)          AWS
   |                       |                     |
   |-- DSoftBus POST -->   |                     |
   |   {hr: 120,           |                     |
   |    steps: 7500}       |                     |
   |                       |-- HTTPS POST -->    |
   |                       |   (batched)         |
   |                       |                     |
   |                       |   <-- JSON --       |
   |   <-- DSoftBus --     |   {mood: "tired"}   |
   |   {pet_state}         |                     |
```

### 2.4 First End-to-End Test (2 hours)

**Milestone**: Real sensor data → Bedrock → Pet responds

**Test Scenario**:
1. Put on watch, start walking
2. HR rises to 110 bpm
3. Data sent to Bedrock Agent
4. Agent returns: `{mood: "active", message: "Great pace! Keep it up!"}`
5. Pet animation changes to "running"
6. Notification appears on watch

**Success Criteria**: Complete loop works within 5 seconds.

---

## Phase 3: The Brain (Hours 18-30)

**Objective**: Add data science and predictive capabilities.

### 3.1 SageMaker Fatigue Model (4 hours)

**Owner**: Data Science Developer

**Tasks**:
```
1. Create synthetic training data:
   - Features: HR, HRV, steps, sleep, time_since_last_workout
   - Label: fatigue_score (0-100)
2. Train Random Forest model in SageMaker notebook
3. Deploy to endpoint
4. Create Lambda function to call endpoint
5. Integrate with Bedrock Agent workflow
```

**Data Pipeline**:
```
Raw Sensors → Feature Engineering → SageMaker Endpoint → Fatigue Score (0-100)
                                                              ↓
                                                    Bedrock Agent uses this in reasoning
```

**Example**:
```python
# SageMaker inference
input = {
    'hr': 85,
    'hrv': 35,  # Low HRV = fatigue
    'sleep_hours': 5.5,
    'steps_today': 12000
}

prediction = model.predict(input)
# Output: {'fatigue_score': 78, 'recommendation': 'rest'}
```

### 3.2 Context-Aware Reasoning (3 hours)

**Owner**: Backend Developer

**Tasks**:
```
1. Enhance Bedrock Agent with Knowledge Base:
   - Upload sports science docs (training zones, recovery protocols)
   - Upload motivational psychology research
2. Implement RAG (Retrieval Augmented Generation):
   - Agent cites sources when giving advice
3. Add user profile (age, fitness level, goals) to prompt
```

**Enhanced Prompt**:
```
You are a virtual pet health coach. User profile:
- Age: 28, Fitness Level: Intermediate
- Goal: Run a half-marathon in 3 months
- Recent sleep: 6.5 hrs (below target)
- Current HR: 165 bpm (Zone 4)

Based on fatigue score of 78/100, what should the pet say and do?
Cite relevant sports science if applicable.
```

### 3.3 Agentic Actions Implementation (5 hours)

**Owner**: Full-Stack Developer

**Tasks**:
```
1. Define Action APIs:
   POST /api/calendar/modify
   POST /api/watch/set_alarm
   POST /api/watch/haptic_pattern
2. Implement Bedrock Agent Action Groups calling these APIs
3. Create user confirmation flow:
   - Agent proposes action → Watch shows approval dialog
   - User accepts/rejects → Feedback to agent
4. Test proactive scenario
```

**Example Agentic Flow**:
```
1. Input: {sleep: 4hrs, scheduled_workout: "HIIT 6PM"}
2. Agent reasoning: "User severely under-rested, high injury risk"
3. Agent action: modify_calendar(workout_id, new_type="yoga")
4. Watch notification: "I changed your HIIT to gentle yoga. You need recovery. OK?"
5. User approves → Action confirmed
```

---

## Phase 4: The Agent (Hours 30-40)

**Objective**: Make the system truly autonomous and handle edge cases.

### 4.1 Multi-Modal Interaction (3 hours)

**Tasks**:
```
1. Implement voice output:
   - Text-to-speech on watch for coaching cues
   - "You're in Zone 5, slow down!"
2. Add user voice input (if time permits):
   - "How am I doing?" → Agent responds with analysis
3. Refine haptic vocabulary:
   - Heartbeat pattern for breathing exercises
   - Escalating alerts for dangerous HR
```

### 4.2 Edge Case Handling (3 hours)

**Critical Scenarios**:
```
1. Network loss during workout:
   - Fallback to on-watch rule-based logic
   - Queue cloud sync for later
2. Sensor anomaly (HR = 0 or 250):
   - Detect and ignore outliers
   - Prompt user to re-seat watch
3. Battery < 15%:
   - Switch to low-power mode (static pet, 5-min updates)
```

### 4.3 Privacy & Transparency (2 hours)

**Tasks**:
```
1. Create "Data Flow" settings screen:
   - Show what data is sent to cloud (HR, GPS, etc.)
   - Toggle granular permissions
2. Add "Why did you do that?" feature:
   - User taps pet → See agent's reasoning
   - "I suggested rest because your HRV dropped 40% and..."
3. Implement local-first mode (no cloud, basic rules only)
```

### 4.4 Polish & Tuning (2 hours)

**Tasks**:
```
1. Optimize battery life:
   - Reduce sensor sampling in ambient mode
   - Batch network requests
2. Tune animation frame rates
3. Add sound effects (if appropriate)
4. A/B test pet personalities (supportive vs. challenging)
```

---

## Phase 5: Polish & Demo Prep (Hours 40-48)

**Objective**: Create compelling demo and presentation materials.

### 5.1 Demo Video Production (3 hours)

**Script**:
```
Scene 1 (0:00-0:30): "The Problem"
- Footage of confusing fitness app graphs
- Voiceover: "Health data is overwhelming..."

Scene 2 (0:30-1:30): "The Solution"
- Watch face showing cute pet
- User goes for run, pet animates in real-time
- Voiceover: "Meet your AI health companion..."

Scene 3 (1:30-2:30): "The Magic - Agentic AI"
- User is tired, pet detects it BEFORE user realizes
- Watch shows: "I'm changing your workout to recovery mode"
- Voiceover: "It doesn't just track, it acts..."

Scene 4 (2:30-3:00): "The Tech"
- Architecture diagram animation
- DSoftBus, Bedrock, SageMaker logos
- Voiceover: "Built on OpenHarmony and AWS Bedrock..."
```

### 5.2 Pitch Deck (2 hours)

**Slides** (Max 10):
1. **Title**: AI Tamagotchi Coach
2. **Problem**: Data overload + lack of autonomy in health apps
3. **Solution**: Emotional bonding + proactive AI
4. **Demo**: Video embed or live demo
5. **Architecture**: Edge-Cloud diagram showing DSoftBus
6. **Huawei Value**: Sensor fusion (X-TAP, HR, GPS, Gyro) + OpenHarmony showcase
7. **Reply Value**: Bedrock Agents + SageMaker + Agentic Loop
8. **Innovation**: First LLM-powered companion on OpenHarmony
9. **Market**: Blue Ocean (no competitors with this combo)
10. **Future**: Roadmap (social features, multi-device, clinical trials)

### 5.3 Live Demo Rehearsal (2 hours)

**Demo Flow** (5 minutes):
1. **Intro** (30s): Show watch idle state, pet sleeping
2. **Wake Up** (1m): Tap watch, pet wakes, shows sleep score
3. **Start Workout** (2m): Begin running (on treadmill or in place)
   - HR rises → Pet animation changes
   - Voice coaching: "Good pace!"
4. **Agentic Intervention** (1m): Simulate fatigue
   - Agent detects elevated HR + low HRV
   - Pet says: "Let's slow down, your body needs rest"
   - Shows calendar modification
5. **Q&A Prep** (30s): Reset for questions

**Backup Plan**: If live demo fails, have video ready.

### 5.4 Code Cleanup & Documentation (1 hour)

**Tasks**:
```
1. Add README to each directory
2. Comment complex algorithms
3. Create ARCHITECTURE.md with diagrams
4. Ensure GitHub repo is public and presentable
5. Add demo video to README
```

---

## Risk Mitigation Strategies

### High-Risk Items & Contingencies

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| DSoftBus doesn't work | Medium | Critical | Fallback to HTTP via phone WiFi hotspot |
| AWS Bedrock access denied | Low | Critical | Use direct Anthropic API (non-agent mode) |
| Watch won't connect to DevEco | Medium | High | Develop on phone emulator, deploy to watch last 6 hours |
| Animations too slow on watch | Medium | Medium | Use static images with state changes only |
| No time for SageMaker model | High | Medium | Use simple rule-based fatigue calc instead |

### "Cut Scope" Priority Order

If behind schedule, cut in this order:
1. ~~Voice input~~ (keep voice output only)
2. ~~SageMaker predictive model~~ (use Bedrock for all reasoning)
3. ~~Calendar integration~~ (just show recommendations, don't auto-modify)
4. ~~Chronic condition use case~~ (focus on athlete use case only)
5. ~~GPS/elevation features~~ (HR and steps only)

**Non-Negotiable Core**:
- Pet responds to heart rate changes
- Bedrock Agent demonstrates autonomous reasoning
- Live demo on physical watch works

---

## Parallel Workstream Strategy

**Team of 3-4 people** can work simultaneously:

### Workstream A: Watch Frontend
- **Who**: Frontend Dev + Designer
- **Focus**: UI/UX, animations, Sport Face
- **Blocker**: Needs sensor data structure from Workstream B

### Workstream B: Sensor & Integration
- **Who**: Embedded/Hardware Dev
- **Focus**: SensorServiceKit, DSoftBus, Watch-Phone bridge
- **Blocker**: Needs API endpoint from Workstream C

### Workstream C: Cloud Backend
- **Who**: Backend/AI Dev
- **Focus**: Bedrock Agent, SageMaker, Lambda, API Gateway
- **Blocker**: None (can use mock data)

### Workstream D: Data Science (Optional if 4th person)
- **Who**: Data Scientist
- **Focus**: SageMaker model, feature engineering
- **Blocker**: Needs real sensor data (but can use synthetic initially)

**Sync Points**: Every 6 hours (after each phase), integrate and test together.

---

## Daily Standup Questions (During Hackathon)

Ask every 6 hours:

1. **What did you complete since last sync?**
2. **What are you working on next?**
3. **What's blocking you?** (Resolve immediately)
4. **Do we need to cut scope?** (Be ruthless)

---

## Success Metrics

**Minimum Viable Demo (to avoid embarrassment)**:
- ✅ Pet visible on watch
- ✅ Heart rate changes pet animation
- ✅ One Bedrock API call succeeds
- ✅ Can explain architecture clearly

**Competitive Demo (top 10)**:
- ✅ Above + End-to-end working (watch → cloud → watch)
- ✅ Voice coaching during simulated workout
- ✅ One agentic action (e.g., notification based on fatigue)

**Winning Demo (top 3)**:
- ✅ Above + SageMaker predictive model integrated
- ✅ Proactive calendar modification shown
- ✅ Polished video demo
- ✅ Clear articulation of "Blue Ocean" market position
- ✅ Judges say "I would actually use this"

---

## Post-Hackathon Roadmap (If Continuing)

### Month 1: Beta Testing
- Recruit 20 beta testers (mix of athletes and chronic condition users)
- Collect 2 weeks of real-world data
- Iterate on pet personality and intervention timing

### Month 2: Clinical Validation
- Partner with sports medicine clinic
- A/B test: App vs. No App on recovery outcomes
- Publish whitepaper

### Month 3: Ecosystem Expansion
- Port to Huawei Phone (larger screen, more UI space)
- Add social features (pet "playdates" compare progress with friends)
- Integrate with Huawei Health ecosystem (if strategically valuable)

### Month 6: Commercialization
- Freemium model: Basic pet free, premium features ($5/month)
- Enterprise partnerships (corporate wellness programs)
- Pitch to VCs for Series A

---

## Key Contacts & Resources

### Technical Support
- **Huawei OpenHarmony Discord**: [Link from challenge docs]
- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock/
- **DevEco Studio Troubleshooting**: https://developer.huawei.com/consumer/en/doc/

### AI APIs
- **Claude Code Terminal Helper**: `python tools/ai_helper.py ask "question"`
- **Anthropic Docs**: https://docs.anthropic.com/
- **Gemini Docs**: https://ai.google.dev/docs

### Team Communication
- **Slack/Discord**: [Setup team channel]
- **GitHub Repo**: https://github.com/[your-repo]
- **Shared Drive**: [For demo video assets]

---

## Appendix: Code Snippets

### A. Complete Pet State Machine

```arkts
enum PetMood {
  SLEEPING = 'sleeping',
  IDLE = 'idle',
  HAPPY = 'happy',
  ACTIVE = 'active',
  TIRED = 'tired',
  CONCERNED = 'concerned'
}

class PetStateManager {
  @State currentMood: PetMood = PetMood.IDLE
  @State heartRate: number = 70
  @State stepCount: number = 0
  @State fatigueScore: number = 0

  updateState() {
    // Rule-based fallback (when cloud unavailable)
    if (this.heartRate < 60 && this.stepCount < 100) {
      this.currentMood = PetMood.SLEEPING
    } else if (this.heartRate > 140) {
      this.currentMood = PetMood.TIRED
    } else if (this.heartRate > 100) {
      this.currentMood = PetMood.ACTIVE
    } else if (this.fatigueScore > 70) {
      this.currentMood = PetMood.CONCERNED
    } else {
      this.currentMood = PetMood.HAPPY
    }
  }

  updateFromCloud(cloudState: any) {
    // Cloud AI overrides rules
    this.currentMood = cloudState.mood
  }
}
```

### B. Bedrock Agent Invocation (Python)

```python
import boto3
import json

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='eu-central-1')

def invoke_tamagotchi_agent(user_data):
    response = bedrock_agent_runtime.invoke_agent(
        agentId='YOUR_AGENT_ID',
        agentAliasId='YOUR_ALIAS_ID',
        sessionId=user_data['user_id'],
        inputText=json.dumps({
            'biometrics': user_data['biometrics'],
            'context': user_data.get('context', ''),
            'user_profile': user_data.get('profile', {})
        })
    )

    # Parse streaming response
    result = ''
    for event in response['completion']:
        if 'chunk' in event:
            result += event['chunk']['bytes'].decode()

    return json.loads(result)
```

---

**Last Updated**: 2025-11-22
**Next Review**: At each phase boundary during hackathon
