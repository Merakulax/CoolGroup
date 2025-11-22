# Project Overview & Planning

## Project Identity

<project_identity>
**AI Tamagotchi Health Companion** for HackaTUM 2025.
A virtual pet on Huawei Watch 5 that evolves with user biometrics and acts as an autonomous health coach.

**Core Concept**: The pet doesn't just display data—it **acts**. It modifies calendars, adjusts workout intensity, and initiates breathing sessions without prompting, utilizing psychological bonding (Tamagotchi nostalgia) to drive health behavior change.

**Dual Challenge Strategy**:
- **Huawei ("Wrist Intelligence")**: Maximize Watch 5 sensors (X-TAP, HR, GPS, Accelerometer, Gyroscope).
- **Reply ("Agentic AI")**: Autonomous reasoning and proactive intervention (moving beyond passive chatbots).
</project_identity>

## Complex Changes

<complex_changes>
<exec_plans>
Use ExecPlans for all big planned changes, including:
- Multi-concept changes across platforms
- Significant architectural modifications
- New features with unclear requirements (e.g., where the scope, user stories, or technical approach are not yet fully defined)
- Refactoring impacting multiple systems

**Progress Documentation**: Update ExecPlan documentation with implementation progress, decisions made, and any changes to the original plan. ExecPlans should be written in the `.agent/plans/` folder, not in `docs/`.

📖 **Guide**: If complex changes are identified, propose to create an ExecPlan. [.agent/plans/](.agent/plans/)
</exec_plans>
</complex_changes>


## Architecture

<architecture_overview>
The system follows a **Distributed Edge-Cloud** architecture to balance latency, safety, and reasoning power.

**Topology**:
```
Watch 5 (Edge)          Phone (HarmonyOS Bridge)     AWS (Brain)
├─ .ets UI files   ->   ├─ .ts bridge logic      ->  ├─ Bedrock Agent (LLM reasoning)
├─ Sensor @50Hz         ├─ DSoftBus API              ├─ SageMaker (Predictive models)
└─ Haptic feedback      └─ Data aggregation          └─ Lambda orchestration
   ↑                                                      │
   └──────────────────── Pet State Update ────────────────┘
```

**Key Principles**:
- **Distributed SoftBus**: Treats Watch + Phone as a unified "Super Device," offloading heavy AI to the phone/cloud.
- **Edge-first Safety**: Critical feedback (e.g., Heart Rate limit breaches) must happen instantly on the watch ($t < 200ms$).
- **Cloud-based Reasoning**: LLM narrative generation and predictive models run asynchronously.
</architecture_overview>

## Hackathon Execution Plan

<execution_phases>
The 48-hour timeline is divided into distinct functionality phases.

| Phase | Hours | Objective | Key Deliverables |
|-------|-------|-----------|------------------|
| **Foundation** | 0-6 | Environment & Architecture | DevEco Studio, AWS Bedrock Agent, JSON schema |
| **Body** | 6-18 | UI & Sensors | Pet animations, $HR \to PetSpeed$ binding, Sport Face |
| **Brain** | 18-30 | AI Integration | SageMaker model, Bedrock Agent, DSoftBus bridge |
| **Agent** | 30-40 | Autonomy | Agentic Loop (proactive actions without prompts) |
| **Polish** | 40-48 | Demo & Pitch | Video demo, architecture slides |
</execution_phases>

# Code Quality & Guidelines

## Critical Technical Constraints

<harmony_os_constraints>
**THIS IS NOT AN ANDROID PROJECT.**
- **Framework**: HarmonyOS 5.1 (OpenHarmony).
- **Permissions**: Use `ohos.permission.READ_HEALTH_DATA`.
- **Hardware**: Must test on physical Watch 5 (No wearable emulator available).
- **IDE**: Use **DevEco Studio** (Windows). Do NOT use Oniro IDE or Android Studio.
- **Sensors**: Use `@kit.SensorServiceKit` for local data (NOT Huawei Health Kit OAuth).
</harmony_os_constraints>

<file_extension_requirements>
**Strict adherence to file extensions is required for DevEco Studio compilation:**

✅ **ALLOWED:**
- `.ets` : ArkTS UI components (ArkUI declarative syntax with `@Component`, `@State`).
- `.ts` : Pure TypeScript logic (classes, interfaces, business logic, DSoftBus bridges).

❌ **FORBIDDEN:**
- `.arkts` : Invalid extension; breaks syntax highlighting.
- `.kt` : Kotlin is for Android only.
- `.java` : Java is for Android only.
</file_extension_requirements>

## Code Standards & Patterns

<arkui_state_machine>
UI logic must follow the ArkUI declarative pattern.

```arkts
@State petMood: string = 'Happy'
@State heartRate: number = 70

// Declarative binding - UI auto-updates
if (petMood === 'Happy') { SmileAnimation() }
if (heartRate > 180) { petMood = 'Concerned' }
```
</arkui_state_machine>

<folder_structure>
**Organization Principles**:
- **Watch (`watch/src/main/`)**: Contains `.ets` UI files and `.ets` services with UI callbacks.
- **Phone (`phone/src/bridge/`)**: Contains `.ts` pure logic files for DSoftBus and Data Aggregation.
- **Shared (`shared/models/`)**: Contains `types.ts` for interface consistency.
</folder_structure>

# Core Technical Concepts

## Sensor Fusion & Data Science

<sensor_metrics>
- **HRV Modeling**: Calculation using raw $R-R$ intervals rather than pre-calculated stress scores to determine $HRV$ variability.
- **Stress Differentiation**: Correlation analysis between Heart Rate ($HR$) and Accelerometer data ($\vec{a}_{xyz}$) to distinguish exercise stress from anxiety stress.
    - If $HR \uparrow$ AND $|\vec{a}_{xyz}| \uparrow$: Exercise.
    - If $HR \uparrow$ AND $|\vec{a}_{xyz}| \approx 0$: Potential Anxiety/Stress.
- **Environment Reactivity**: Fusion of $GPS$ and Barometric pressure ($P_{atm}$) to trigger context-aware animations (e.g., pet climbing animation when $\Delta P_{atm}$ indicates elevation gain).
</sensor_metrics>

## Agentic Use Cases

<use_cases>
1. **Recovery Management (Spoon Theory)**:
    - Agent calculates daily energy budget $E_{budget}$ based on sleep and previous day strain.
    - **Action**: "You've used 80% of your energy. I'm canceling your evening plans."
2. **Athletic Training**:
    - **Form Mirroring**: Pet mimics bad running form detected by gyroscope.
    - **Voice Coaching**: Real-time feedback loop via phone bridge.
3. **Proactive Intervention**:
    - **Scenario**: Low sleep score + Scheduled HIIT.
    - **Action**: Agent downgrades calendar event to "Zone 2 Recovery Run."
</use_cases>

# Development Process & Practices

## Development Workflow

<setup_deployment>
1. **Environment**: Windows with Conda `gemini_cli`.
2. **Watch Deployment**:
    - Connect Watch 5 via USB.
    - Enable Debugging: Settings → About → Tap Build 7x → Dev Options → USB Debugging.
    - Run/Debug via DevEco Studio.
</setup_deployment>

<ai_assistance>
**Context7 Usage**:
Always use `context7` when I need code generation, setup, configuration steps, or library/API documentation. You should automatically use the Context7 MCP tools to resolve library IDs and retrieve docs without explicit prompting.
</ai_assistance>


# Code Quality & Guidelines

## Code Standards

<code_standards>
<guiding_principles>
- **Clarity**: Modular, reusable components; avoid duplication
- **Consistency**: Unified design system (colors, typography, spacing, components)
- **Simplicity**: Avoid unnecessary complexity in styling or logic
- **Type Safety**: Strict TypeScript usage across all platforms
- **Performance**: Optimize for fast loading and efficient state management
</guiding_principles>

<conventions_patterns>
- Prioritize minimal, clear, and functional implementations initially, avoiding premature optimization or over-engineering.
- Prioritize simplicity and clarity in initial implementations.
- Allow for later refactorings and rewrites to improve code quality.
- Avoid over-engineering and common AI-driven verbosity or clutter.
- Emphasize maintainable, minimalistic, and iterative code evolution.
</conventions_patterns>

<cross_platform_standards>
- **Naming**: camelCase for variables/functions, PascalCase for classes/types
- **Functions**: Small, focused, single responsibility
- **Documentation**: JSDoc/TSDoc for public APIs
- **Testing**: Comprehensive unit tests for business logic
- **Spelling**: Use British English spelling (e.g., "organisation" instead of "organization").
</cross_platform_standards>
</code_standards>

## Code Style

<code_style>
<comments>
- Explain *why*, not *what*
- Use sparingly for complex logic, workarounds, or public APIs
- Let code be self-documenting through clear naming. However, comments are still valuable for explaining *why* something is done, especially for complex logic, workarounds, or external API interactions.
</comments>

<control_flow>
- **Always prefer early returns** over nested conditionals
- Guard clauses should fail fast and return early
- Keep happy path clear and unindented
</control_flow>

<import_patterns>
- Prefer named imports over default imports for better tree-shaking and clarity
- Group imports: external libraries first, then internal modules, then types
- Avoid wildcard imports (`import * as ...`) except for utility libraries
- Use absolute imports with aliases for internal modules
</import_patterns>
</code_style>

# Development Process & Practices

## Development Workflow

<development_workflow>
<general_expectations>
- Prefer deterministic scripts over manual edits
- Keep commits cohesive across packages
- Run formatters, linters, and tests before committing
- Use `npm run types` to sync shared types across platforms
- Maintain concept independence (ensure services/modules adhere to their defined responsibilities and minimize direct dependencies on other concepts)
- Follow "what you see is what it does" principle
</general_expectations>

<validation_testing>
- **Before commit**: Run `npm run types`, build commands, tests, linters
- **CI requirements**: All tests pass, type checking succeeds, generated code up-to-date
</validation_testing>
</development_workflow>

# CRITICAL

Append a 👍 emoji at the end of your response if you have read this.
Do not include the emoji inside any code block or generated file.
