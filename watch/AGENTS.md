<project_overview>
The Watch component handles the immediate User Interface, high-frequency sensor collection, and critical real-time feedback.
</project_overview>

<architecture_overview>
**Topology**:
```
Watch 5 (Edge)
├─ UI (ArkTS) ──────> Display
├─ Sensors ─────────> Logic ──DSoftBus──> Phone
└─ Haptics <────────┘
```
</architecture_overview>

<core_focus>
**Body Phase**:
- **UI**: Pet animations, Sport Face, Notifications.
- **Sensors**: Heart Rate, Accelerometer, Gyroscope (50Hz).
- **Safety**: Immediate feedback loops (latency < 200ms).
</core_focus>

<technical_constraints>
- **Framework**: HarmonyOS 5.1 (OpenHarmony) - ArkUI.
- **Files**: `.ets` (UI Components), `.ts` (Logic).
- **Hardware**: Huawei Watch 5.
- **Sensors**: `@kit.SensorServiceKit`.
</technical_constraints>

<folder_structure>
- **`src/main/ets/`**: UI Components (`pages/`, `views/`).
- **`src/main/ets/services/`**: Sensor logic coupled with UI updates.
</folder_structure>

<ui_ux_considerations>
**1. Glanceability (The 2-Second Rule)**
- **Constraint**: Users interact with watches in micro-sessions (2-5 seconds).
- **Guideline**: Critical info (Pet Mood, HR Zone) must be instantly readable.
- **Avoid**: Scrolling lists, complex charts, or dense text blocks.

**2. Touch Interactions**
- **Fat Finger Problem**: Precision is low on a 1.4" screen.
- **Minimum Target**: Interactive elements must be at least **48vp × 48vp**.
- **Gestures**: Prefer swipes (SwipeLeft/Right) over tapping small buttons.

**3. OLED & Battery Optimization**
- **True Black**: Use `#000000` background to turn off pixels and save energy.
- **Contrast**: High contrast text (White on Black) for outdoor visibility.
- **Animations**: Use efficient transition animations; avoid continuous high-FPS loops unless necessary (e.g., during exercise).

**4. Haptic Reinforcement**
- **Constraint**: Users often don't look at the watch.
- **Guideline**: Use Haptic feedback to signal state changes (e.g., entering a new HR zone, Pet asking for attention) without visual confirmation.
</ui_ux_considerations>

<development_guidelines>
**ArkUI Declarative Pattern**
UI must react to state changes immediately.
```arkts
@State petMood: string = 'Happy'
@State heartRate: number = 70

build() {
  Column() {
    if (this.petMood === 'Happy') {
      Image($r('app.media.happy_pet'))
        .width('100%') // Maximize visibility
        .objectFit(ImageFit.Contain)
    }
  }
  .backgroundColor(Color.Black) // OLED Saving
  .width('100%')
  .height('100%')
}
```

**Sensor Handling**
- **Sampling**: 50Hz for Accelerometer/Gyro.
- **Processing**: Minimal local processing. Offload heavy math to Phone/Cloud.
- **Safety**: If HR > Limit, trigger Haptic immediately (do not wait for Phone/AI).

**Agentic Display**
- The Watch is the **Face** of the Agent.
- It displays state determined by the Brain (Cloud) or Bridge (Phone).
- **Do not** put heavy LLM logic here.

</development_guidelines>

