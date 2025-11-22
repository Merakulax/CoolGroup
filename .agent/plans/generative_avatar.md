# Execution Plan: Generative Avatar Endpoint (Vertex AI / Google Gen AI SDK) [COMPLETED]

## Objective
Create an API endpoint that generates a dynamic visual representation (avatar) of the user's current state. This system fuses recent physiological data (HR, Sleep, Stress) with the user's base avatar image using **Google Gen AI SDK** and **Vertex AI**.

## Scope
- **Infrastructure:** AWS (Lambda, API Gateway, S3, Layers) + **Google Cloud (Vertex AI API)**.
- **Terraform:** Configure `google` provider and API Gateway routes.
- **Backend Logic:** `avatar_generator` Lambda using `google-genai` SDK.
- **Data Flow:** Fetch User Profile -> Construct Prompt -> Call Gemini/Imagen -> Save to S3 -> Return Presigned URL.

## Phase 1: Infrastructure (Terraform) [COMPLETED]
1.  **Google Cloud Setup**:
    - Enabled API: `aiplatform.googleapis.com`.
    - **Authentication**: Switched to **API Key** (manual creation) due to Org Policy constraints blocking Service Account Keys and Workload Identity Pool creation.
2.  **Lambda Function**:
    - `avatar_generator`: Deployed with Env Vars (`GCP_API_KEY`, `GCP_PROJECT_ID`).
    - **Layer**: Created `aws_lambda_layer_version` containing `google-genai` and dependencies to solve package size limits.
3.  **API Gateway**:
    - Route: `GET /avatar/current-state/{user_id}` -> `avatar_generator`.

## Phase 2: Backend Implementation [COMPLETED]
1.  **Library**: Switched from `google-cloud-aiplatform` to `google-genai` SDK (v1.52.0).
2.  **Logic**:
    - Initialize `genai.Client` with API Key.
    - Construct prompt based on health metrics (Sleep, Stress, HR).
    - Call model `imagen-3.0-generate-001` (fallback to `gemini-2.5-flash` for text if needed).
    - Save generated image to S3 bucket `tamagotchi-health-avatars-{env}`.
    - Return Presigned S3 URL.

## Phase 3: Verification [PENDING]
1.  **Test**:
    - Call `GET /avatar/current-state/{user_id}`.
    - Verify JSON response contains `image_url`.
    - Verify image URL loads a generated PNG.

## Key Assumptions
- GCP Project `hackatum25mun-1040` has `aiplatform.googleapis.com` enabled.
- API Key provided has permissions to call Vertex AI.