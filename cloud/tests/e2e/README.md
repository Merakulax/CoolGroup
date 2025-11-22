# Cloud End-to-End (E2E) Tests

These tests verify the system against a **live AWS deployment**. 
They interact with real API Gateway endpoints, Lambda functions, and DynamoDB tables.

**⚠️ WARNING:** These tests create real data and consume AWS credits (Bedrock/Lambda).

## Prerequisites

1. **Deploy the Infrastructure**:
   ```bash
   cd cloud/infrastructure/terraform
   terraform apply
   ```

2. **Configure AWS Credentials**:
   Ensure your `~/.aws/credentials` or environment variables are set.

## Running the Tests

You can run the tests using `uv` and `pytest`.

### Option 1: Auto-Discovery (Recommended)
If you have AWS credentials configured, the test runner can verify the CloudFormation/Terraform stack outputs to find the API URL.

```bash
# Run E2E tests
 uv run --with pytest --with boto3 --with requests pytest cloud/tests/e2e/test_live_deployment.py --stack-name tamagotchi-health-dev
```

### Option 2: Manual Configuration
If auto-discovery fails, provide the API URL directly.

```bash
 uv run --with pytest --with boto3 --with requests pytest cloud/tests/e2e/test_live_deployment.py \
  --api-url https://xxxxxx.execute-api.eu-central-1.amazonaws.com \
  --stack-name tamagotchi-health-dev
```

## What is Tested?

1.  **Connectivity**: `POST /echo` to verify API Gateway is up.
2.  **Full AI Loop**:
    *   Creates a random test user.
    *   Ingests **Stress** sensor data (High HR, Low Motion).
    *   Polls DynamoDB to verify the **Bedrock Agent** correctly identified the state as `STRESS`.
3.  **Demo Overrides**:
    *   Verifies the `POST /demo/trigger` endpoint allows manual state forcing.

