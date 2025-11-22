# Contributing Guide

Guidelines for CoolGroup team members working on the AI Tamagotchi Health Companion.

## Quick Start

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repo-url>
   cd CoolGroup
   ```

2. **Choose your module** (see `docs/TEAM_ROLES.md`)
   - Watch: `cd watch`
   - Phone: `cd phone`
   - Cloud: `cd cloud`

3. **Follow module-specific setup** (see `README.md` in each module)

4. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Branch Naming Convention
- **Features**: `feature/sensor-integration`
- **Bug fixes**: `fix/dsoftbus-reconnect-issue`
- **Documentation**: `docs/update-architecture`

### Commit Message Format
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(watch): implement heart rate sensor integration
fix(phone): resolve DSoftBus reconnection bug
docs(cloud): update Lambda deployment instructions
```

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat(watch): add pet animation system"
   ```

3. **Push to remote**
   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request on GitHub**
   - Add clear description of changes
   - Reference any related issues
   - Request review from relevant developer

5. **Address review feedback**
   - Make requested changes
   - Push updates to same branch
   - Re-request review

6. **Merge after approval**
   - Squash commits if multiple small commits
   - Delete feature branch after merge

## Shared Contract Updates

**CRITICAL**: Coordinate with all team members before changing contracts!

### Process for Contract Changes

1. **Propose change** in team chat (Slack/Discord)
   ```
   "I need to add 'bloodOxygen' field to SensorPayload.
    Affects: Watch (data collection), Phone (passthrough), Cloud (storage).
    Breaking change: NO (optional field)
    ETA: Ready to implement in 2 hours"
   ```

2. **Wait for approval** from affected developers

3. **Update contract schema**
   ```bash
   # Edit JSON schema
   vim shared/contracts/sensor_data.json
   ```

4. **Regenerate models** for all languages
   ```bash
   # TypeScript (Watch)
   # Update shared/models/typescript/sensor_data.ts

   # Kotlin (Phone)
   # Update shared/models/kotlin/SensorPayload.kt

   # Python (Cloud)
   # Update shared/models/python/sensor_data.py
   ```

5. **Commit all changes together**
   ```bash
   git add shared/
   git commit -m "feat(shared): add bloodOxygen to SensorPayload

   - Updated JSON schema with optional bloodOxygen field
   - Regenerated TypeScript, Kotlin, Python models
   - Non-breaking change (optional field)

   Approved by: @watch-dev, @phone-dev, @cloud-dev"
   ```

6. **Notify team** that contract is updated
   ```
   "SensorPayload contract updated on main. Pull latest changes before continuing work."
   ```

## Code Style Guidelines

### TypeScript/ArkTS (Watch)
```typescript
// Use PascalCase for interfaces
export interface PetState {
  mood: PetMood;
  energy: number;
}

// Use camelCase for functions/variables
function updatePetMood(heartRate: number): void {
  // ...
}
```

### Kotlin (Phone)
```kotlin
// Use PascalCase for classes
data class SensorPayload(
    val heartRate: Int,
    val timestamp: Long
)

// Use camelCase for functions/variables
fun aggregateSensorData(batch: List<SensorPayload>) {
    // ...
}
```

### Python (Cloud)
```python
# Use PascalCase for classes
class SensorPayload:
    def __init__(self, heart_rate: int):
        self.heart_rate = heart_rate

# Use snake_case for functions/variables
def process_sensor_batch(batch: List[dict]) -> dict:
    # ...
```

## Testing Requirements

### Watch (ArkTS)
```bash
# Run tests in DevEco Studio
# Test → Run All Tests
```

### Phone (Kotlin)
```bash
./gradlew test
./gradlew connectedAndroidTest  # Requires physical device
```

### Cloud (Python)
```bash
cd cloud
pytest tests/
pytest tests/integration/ --aws  # Integration tests
```

## Common Issues & Solutions

### Issue: DSoftBus not connecting
**Solution**: Ensure Watch and Phone are paired via Huawei Health app

### Issue: Lambda function timeout
**Solution**: Increase timeout in `sam-template.yaml`:
```yaml
Timeout: 30  # Increase from default 3 seconds
```

### Issue: Git merge conflicts in shared/contracts
**Solution**:
1. Coordinate in team chat before making changes
2. Pull latest before starting work
3. Use `git pull --rebase` to avoid merge commits

## Documentation

### When to Update Docs

- **Adding new feature**: Update module README
- **Changing architecture**: Update `docs/ARCHITECTURE.md`
- **New API endpoint**: Update API documentation
- **Shared contract change**: Update `shared/README.md`

### Documentation Standards

- Use Markdown for all docs
- Include code examples where relevant
- Keep line length under 100 characters
- Add diagrams for complex flows (use ASCII art or tools like Mermaid)

## Integration Testing

### End-to-End Test Flow

1. **Watch sends mock data**
   ```arkts
   const mockPayload: SensorPayload = {
     heartRate: 180,  // High HR to trigger agent
     timestamp: Date.now()
   };
   // Send via DSoftBus
   ```

2. **Phone logs received data**
   ```kotlin
   println("Received: $payload")
   // Verify batching works
   ```

3. **Cloud processes and responds**
   ```python
   # Check CloudWatch logs for Lambda execution
   # Verify DynamoDB has new entry
   # Check WebSocket sent pet state update
   ```

4. **Watch receives pet update**
   ```arkts
   // Verify pet mood changed to "Concerned"
   // Verify haptic feedback triggered
   ```

## Emergency Rollback

If a change breaks integration:

```bash
# Identify last working commit
git log --oneline

# Revert to that commit
git revert <commit-hash>

# Or reset (use with caution)
git reset --hard <commit-hash>
git push --force origin main
```

**IMPORTANT**: Notify team immediately in chat if you need to rollback!

## Resources

- [Project README](../README.md)
- [Architecture Docs](./ARCHITECTURE.md)
- [Team Roles](./TEAM_ROLES.md)
- [Setup Guide](../SETUP.md)

## Questions?

Post in team chat or contact module specialists (see `docs/TEAM_ROLES.md`)
