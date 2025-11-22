<project_overview>
The cloud component acts as the central nervous system, handling heavy AI reasoning, predictive modeling, and state persistence.
</project_overview>

<architecture_overview>
**Topology**:
```
Phone (Bridge) ──HTTPS──> API Gateway ──> Lambda Functions
                                             │
                                             ├─> Bedrock Agent (Qualitative reasoning)
                                             ├─> SageMaker (Quantitative predictions)
                                             └─> DynamoDB (State persistence)

Lambda ──WebSocket──> Phone (Bridge)
```
</architecture_overview>

<core_focus>
- **Brain Phase**: AI Integration (SageMaker, Bedrock, Bridge).
- **Agent Phase**: Autonomy (Agentic Loop, Proactive actions).
</core_focus>

<technical_constraints>
- **Runtime**: Python 3.11+
- **Region**: `eu-central-1` (GDPR compliance).
- **Infrastructure**: AWS SAM or Terraform.
- **Key Services**:
    - **Lambda**: Serverless compute for API & orchestration.
    - **Bedrock**: Claude Sonnet for agentic reasoning.
    - **SageMaker**: XGBoost/PyTorch for specific health models.
    - **DynamoDB**: NoSQL for user/pet state.
</technical_constraints>

<folder_structure>
- **`cloud/lambda/`**: Serverless functions.
    - **`ingest/`**: Data ingestion endpoints (`sensor_ingest.py`).
    - **`orchestrator/`**: Agentic loop logic (`agentic_loop.py`).
- **`cloud/sagemaker/`** *(Planned)*: ML model definitions.
- **`cloud/bedrock/`** *(Planned)*: Agent configurations & prompts.
- **`cloud/infrastructure/`** *(Planned)*: IaC templates (SAM/CloudFormation).
</folder_structure>

<development_guidelines>
**Agentic Loop Implementation**
The core loop triggers on significant sensor data changes:
1.  **Perception**: Aggregate incoming sensor data.
2.  **Reasoning**: Invoke Bedrock Agent with context.
3.  **Planning**: Generate action plan (e.g., "cancel_event", "update_pet_mood").
4.  **Action**: Execute via API/WebSocket to phone.

**Python Standards**
- **Typing**: Use `mypy` compatible type hinting.
- **Dependencies**: Manage via `requirements.txt` per function + root.
- **Testing**: `pytest` for unit/integration tests.

**AWS Patterns**
- **Statelessness**: Lambdas must be stateless; use DynamoDB for state.
- **Async Processing**: Offload heavy ML tasks to async invoke or Step Functions if >30s.
- **Security**: IAM roles with least privilege. No hardcoded credentials.
</development_guidelines>
