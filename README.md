# AI Tamagotchi Health Companion

HackaTUM 2025 - Huawei "Wrist Intelligence" + Reply "Agentic AI" Challenge

## Project Structure

```
CoolGroup/
├── watch/              # HarmonyOS Watch 5 application (ArkTS)
├── phone/              # Phone bridge application (DSoftBus aggregation)
├── cloud/              # AWS backend (Bedrock Agents, SageMaker, Lambda)
├── shared/             # Shared data models and contracts
├── docs/               # Architecture and design documentation
└── tools/              # Development utilities and AI helpers
```

## Team Workflow

**Parallel Development Streams:**
1. **Watch Developer**: Work in `/watch` - HarmonyOS UI, sensors, Sport Face
2. **Phone Developer**: Work in `/phone` - DSoftBus bridge, auth gateway
3. **Cloud Developer**: Work in `/cloud` - AWS Lambda, Bedrock integration

**Shared Contract**: All components communicate via `/shared/contracts` - update interface versions when making breaking changes.

## Quick Start

### Watch Development
```bash
cd watch
# See watch/README.md for DevEco Studio setup
```

### Phone Bridge
```bash
cd phone
# See phone/README.md for setup
```

### Cloud/Backend
```bash
cd cloud
# See cloud/README.md for AWS credentials and deployment
```

## Architecture

```
Watch 5 (Edge)          Phone (Bridge)           AWS (Brain)
├─ Sensor data @50Hz -> ├─ DSoftBus aggregation -> ├─ Bedrock Agent
├─ UI rendering         ├─ Auth gateway          ├─ SageMaker
└─ Haptic feedback      └─ Phone compute         └─ Lambda
   ↑                                                 │
   └─────────────── Pet State Update ────────────────┘
```

See [CLAUDE.md](./CLAUDE.md) for full project context.

## Development Environment

- **Watch**: DevEco Studio (Windows), ArkTS
- **Phone**: TBD (Kotlin/Swift or cross-platform)
- **Cloud**: AWS CLI, Python 3.x, Conda (`gemini_cli`)
- **AI Tools**: Anthropic/Google APIs for terminal assistance

## Key Resources

- [Setup Guide](./SETUP.md) - Environment configuration
- [Architecture](./docs/ARCHITECTURE.md) - Detailed system design
- [Project Context](./tools/context.md) - Original hackathon brief
