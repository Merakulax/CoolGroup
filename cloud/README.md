# Cloud Module - AWS Backend

AWS-based AI brain for the Tamagotchi Health Companion.

## Overview

This module contains the Cloud/Brain component that:
- **Bedrock Agents**: LLM reasoning for agentic loop (Perception → Reasoning → Planning → Action)
- **SageMaker**: Predictive models (fatigue prediction, stress classification, HRV analysis)
- **Lambda Functions**: API endpoints and orchestration
- **DynamoDB**: User state and historical data storage
- **API Gateway**: RESTful API and WebSocket for real-time updates

## Architecture Role

```
Phone ──HTTPS──> API Gateway ──> Lambda Functions
                                      │
                                      ├─> Bedrock Agent (Qualitative reasoning)
                                      ├─> SageMaker (Quantitative predictions)
                                      └─> DynamoDB (State persistence)

Lambda ──WebSocket──> Phone ──DSoftBus──> Watch
```

## Project Structure

```
cloud/
├── lambda/
│   ├── ingest/                 # Data ingestion endpoints
│   │   ├── sensor_ingest.py    # Receive sensor batches
│   │   ├── health_metrics.py   # Process health data
│   │   └── requirements.txt
│   ├── orchestrator/           # Agentic Loop orchestration
│   │   ├── agentic_loop.py     # Main agent coordinator
│   │   ├── bedrock_client.py   # Bedrock Agent integration
│   │   └── requirements.txt
│   └── state_manager/          # Pet state management
│       ├── update_pet_state.py # Update pet based on AI decisions
│       ├── get_pet_state.py    # Retrieve current state
│       └── requirements.txt
├── sagemaker/
│   ├── models/                 # ML model training
│   │   ├── hrv_predictor/      # HRV-based fatigue prediction
│   │   ├── stress_classifier/  # Stress vs exercise classification
│   │   └── energy_budget/      # Spoon theory energy estimation
│   ├── notebooks/              # Development notebooks
│   │   └── data_exploration.ipynb
│   └── inference/              # Deployed endpoints
│       └── model_handler.py
├── bedrock/
│   ├── agents/                 # Bedrock Agent configurations
│   │   ├── health_coach_agent.json
│   │   └── action_planner.json
│   └── prompts/                # LLM prompt templates
│       ├── system_prompt.txt
│       └── action_templates.txt
├── shared/
│   ├── models.py               # Shared data models
│   ├── utils.py                # Helper functions
│   └── config.py               # Configuration
├── infrastructure/
│   ├── cloudformation/         # IaC templates (or Terraform)
│   │   ├── api_gateway.yaml
│   │   ├── lambda_functions.yaml
│   │   └── dynamodb_tables.yaml
│   └── sam-template.yaml       # AWS SAM deployment
└── requirements.txt            # Root dependencies
```

## Technology Stack

- **Runtime**: Python 3.11+
- **AWS Services**:
  - Lambda (Python runtime)
  - Bedrock (Claude Sonnet for agents)
  - SageMaker (XGBoost, PyTorch for models)
  - DynamoDB (NoSQL state storage)
  - API Gateway (REST + WebSocket)
  - S3 (Model artifacts, historical data)
- **Frameworks**:
  - AWS SDK (boto3)
  - LangChain (Bedrock Agent orchestration)
  - SciKit-Learn / PyTorch (ML models)
- **IaC**: AWS SAM or Terraform
- **Region**: eu-central-1 (GDPR compliance)

## Getting Started

### Prerequisites
1. AWS Account with CLI configured
2. Python 3.11+ and conda/venv
3. AWS SAM CLI (for local testing)

### Setup
```bash
cd cloud

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
# Enter: eu-central-1 as region

# Set environment variables
cp .env.example .env
# Edit .env with your AWS resource ARNs
```

### Local Development
```bash
# Test Lambda locally with SAM
sam local start-api

# Invoke specific function
sam local invoke SensorIngestFunction --event events/sensor_batch.json

# Test with local DynamoDB
docker run -p 8000:8000 amazon/dynamodb-local
```

## Key Components

### 1. Lambda - Sensor Ingestion
Receives batched sensor data from phone bridge.

```python
# lambda/ingest/sensor_ingest.py
def handler(event, context):
    sensor_batch = json.loads(event['body'])

    # Validate and store in DynamoDB
    store_sensor_data(sensor_batch)

    # Trigger agentic loop if needed
    if should_trigger_agent(sensor_batch):
        invoke_agentic_loop(sensor_batch)

    return {'statusCode': 200}
```

### 2. Bedrock - Agentic Reasoning
Uses Claude for qualitative health coaching decisions.

```python
# lambda/orchestrator/bedrock_client.py
import boto3

bedrock = boto3.client('bedrock-agent-runtime')

def invoke_health_coach(sensor_summary, user_context):
    response = bedrock.invoke_agent(
        agentId='...',
        agentAliasId='...',
        sessionId=user_id,
        inputText=f"User HRV dropped 20%. Sleep: 5hrs. Scheduled: HIIT workout."
    )

    # Agent decides: "Downgrade to Zone 2 recovery run, cancel evening plans"
    return parse_agent_actions(response)
```

### 3. SageMaker - Predictive Models
Train and deploy ML models for quantitative predictions.

```python
# sagemaker/inference/model_handler.py
class HRVPredictor:
    def predict_fatigue(self, hrv_data):
        # Load deployed SageMaker endpoint
        predictor = sagemaker.predictor.Predictor('hrv-model-endpoint')
        fatigue_score = predictor.predict(hrv_data)
        return fatigue_score
```

### 4. DynamoDB Schema
```python
# User State Table
{
  "user_id": "uuid",
  "pet_state": {
    "mood": "Happy",
    "energy_budget": 100,
    "last_update": "2025-11-22T10:30:00Z"
  },
  "health_metrics": {
    "hrv_trend": [60, 58, 55],  # Last 3 days
    "sleep_hours": [7, 6, 5],
    "stress_level": "moderate"
  }
}
```

## Agentic Loop Implementation

The core AI loop runs every time significant sensor changes occur:

```python
# Perception: Aggregate sensor data
sensor_summary = aggregate_last_hour(sensor_data)

# Reasoning: LLM analyzes situation
bedrock_analysis = bedrock.invoke_agent(sensor_summary, user_context)

# Planning: Generate action plan
action_plan = parse_actions(bedrock_analysis)
# Example: ["downgrade_workout", "schedule_breathing_session", "update_calendar"]

# Action: Execute autonomously
for action in action_plan:
    execute_action(action)  # Modify calendar, send notifications, update pet state
```

## API Endpoints

### REST API
- `POST /api/v1/user/{user_id}/data` - Ingest sensor batch from phone
- `GET /api/v1/user/{user_id}/state` - Get current pet state
- `POST /api/v1/demo/trigger` - Trigger manual action

### WebSocket
- `wss://api.example.com/socket` - Real-time pet state updates to phone

## Deployment

### Deploy with AWS SAM
```bash
# Build Lambda packages
sam build

# Deploy to AWS
sam deploy --guided
# Follow prompts to set stack name, region, etc.
```

### Deploy SageMaker Model
```bash
cd sagemaker/models/hrv_predictor
python train.py  # Train locally
python deploy.py # Deploy to SageMaker endpoint
```

### Environment Variables
Required in Lambda environment:
```
DYNAMODB_TABLE=tamagotchi-user-state
BEDROCK_AGENT_ID=XXXXX
SAGEMAKER_ENDPOINT=hrv-model-endpoint
AWS_REGION=eu-central-1
```

## Brain Simulations & Demo Tools

To facilitate development and showcase the AI reasoning capabilities without physical hardware, we have created a suite of simulation tools.

### 1. Scenario Injector
Simulates immediate physiological events to trigger the State Reactor.
```bash
python lambda/demo/scenario_injector.py --scenario stress
```

### 2. History Seeder
Populates DynamoDB with long-term health trends (e.g., 14 days of burnout data) to test Predictive Models.
```bash
python lambda/demo/history_seeder.py --profile burnout --days 14
```

### 3. Profile Manager
Dynamically switches User Personas to test the Agent's adaptability (e.g., Strict vs. Encouraging Coach).
```bash
python lambda/demo/profile_manager.py --style STRICT --tone direct
```

### 4. Environment Simulator
Injects complex environmental context (Altitude, Weather, Speed) for advanced reasoning.
```bash
python lambda/demo/environment_simulator.py --scenario hike
```

## Testing

### Integration Tests
We have a robust integration test suite that validates the end-to-end logic of the Brain, including:
- **State Reactor Logic**: Verifying correct state transitions (e.g., Stress -> Calm).
- **Persona Injection**: Ensuring the LLM receives the correct system prompt based on user profile.
- **Complex Ingestion**: Verifying that environmental data is correctly parsed and stored.

**Run the tests:**
```bash
uv run --with pytest --with boto3 --with pytest-mock --with moto --with numpy pytest cloud/tests/integration/test_brain_simulations.py
```

## Monitoring

- **CloudWatch Logs**: Lambda execution logs
- **CloudWatch Metrics**: API latency, Lambda invocations, error rates
- **X-Ray**: Distributed tracing for debugging

```bash
# View logs
sam logs -n SensorIngestFunction --tail

# Metrics dashboard
aws cloudwatch get-dashboard --dashboard-name TamagotchiMetrics
```

## Cost Optimization

- **Lambda**: Use ARM Graviton2 for 20% cost savings
- **Bedrock**: Use Claude Haiku for non-critical reasoning (cheaper than Sonnet)
- **SageMaker**: Use Serverless Inference for sporadic traffic
- **DynamoDB**: On-demand billing (not provisioned)

## Resources

- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [SageMaker Python SDK](https://sagemaker.readthedocs.io/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

## Team Member

**Cloud Developer** - Focus areas:
- Lambda function reliability and error handling
- Bedrock Agent prompt engineering
- SageMaker model training and deployment
- API Gateway security (CORS, authentication)
- DynamoDB schema optimization
