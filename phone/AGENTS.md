<project_overview>
The Phone component acts as the intelligent bridge between the real-time Edge (Watch) and the reasoning Brain (Cloud). It aggregates data and handles communication.
</project_overview>

<architecture_overview>
**Topology**:
```
Phone (HarmonyOS Bridge)
├─ DSoftBus <───────> Watch 5
├─ Data Aggregation
└─ HTTPS/WebSocket <──> Cloud (AWS)
```
</architecture_overview>

<core_focus>
**Brain Phase Integration**:
- **DSoftBus**: Reliable communication with Watch.
- **Aggregation**: Batching 50Hz sensor data before Cloud upload.
- **Caching**: Storing Pet State for offline availability.
</core_focus>

<technical_constraints>
- **Framework**: HarmonyOS 5.1 (OpenHarmony) - TypeScript.
- **Files**: `.ts` (Logic/Bridge). No UI focus (background services).
- **Networking**: `connection.NetConnection` (DSoftBus), `http` (AWS).
</technical_constraints>

<folder_structure>
- **`src/main/ts/bridge/`**: DSoftBus handling.
- **`src/main/ts/services/`**: Data aggregation and Cloud API clients.
</folder_structure>

<development_guidelines>
**The "Super Device" Concept**
- Treat Watch + Phone as one unit.
- The Phone provides the compute & network power the Watch lacks.

**Data Pipeline**
1.  **Receive**: Stream from Watch via DSoftBus.
2.  **Aggregate**: Buffer 1-5 seconds of data.
3.  **Ingest**: Send batch to AWS Lambda (`POST /sensor-data`).
4.  **Update**: Receive Pet State updates from Cloud.
5.  **Sync**: Push new State to Watch via DSoftBus.

**Logic Standards**
- **Stateless**: Prefer functional logic for data transformation.
- **Robustness**: Handle connection drops (Watch or Cloud) gracefully.
- **Battery**: Batch network requests to save energy.
</development_guidelines>
