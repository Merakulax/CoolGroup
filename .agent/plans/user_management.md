# Execution Plan: User Management & Onboarding

## Objective
Implement a lightweight user management system to support personalized Tamagotchi experiences. This allows storing user preferences (name, goals) and associating them with specific health data streams. Additionally, support custom avatars (images) for the user/pet to enable future customization.

## Scope
- **Infrastructure:** New `Users` DynamoDB table, S3 Bucket for avatars.
- **Backend API:** Endpoints for creating profiles, retrieving profiles, and uploading avatars.
- **Contracts:** New `user_profile.json` contract.

## Phase 1: Data Modeling
1.  **Create `user_profile.json`**:
    - Fields: `user_id` (UUID), `name` (String), `age` (Int), `health_goals` (List[String]), `pet_name` (String).
    - **New Field**: `avatar_url` (String, optional) - URL to the stored image.
2.  **Generate Python Models**: Create `shared/models/python/user_profile.py`.

## Phase 2: Infrastructure (Terraform)
1.  **DynamoDB Table**:
    - Name: `Users` (Partition Key: `user_id`).
    - Billing: PAY_PER_REQUEST.
2.  **S3 Bucket**:
    - Name: `tamagotchi-avatars-{env}`.
    - Configuration: Private, CORS enabled (for direct browser/phone uploads).
3.  **Lambda Functions**:
    - `user_manager`: Handles CRUD operations for users.
    - **Permissions**: Grant `user_manager` lambda `s3:PutObject` (for presigning) and `s3:GetObject` rights.
4.  **API Gateway**:
    - `POST /users`: Create/Update user profile.
    - `GET /users/{user_id}`: Get user profile.
    - `GET /users/{user_id}/avatar/upload-url`: Generate a presigned S3 PUT URL.

## Phase 3: Backend Implementation
1.  **User Lambda (`cloud/lambda/user/manager.py`)**:
    - `POST /users`: Validate input, save to `Users` table.
    - `GET /users/{user_id}`: Retrieve from `Users` table.
    - `GET /users/{user_id}/avatar/upload-url`:
        - Generate S3 Presigned POST/PUT URL for key `avatars/{user_id}.jpg`.
        - Return URL to client.
        - Client uploads image directly to S3.
        - Client calls `POST /users` to update `avatar_url` (or Lambda triggers on S3 upload to update DB - *Decision: Client update is simpler for MVP*).
2.  **Integration**:
    - Update `orchestrator` to fetch User Profile (e.g., to use the user's name or pet's name in AI prompts).

## Phase 4: Verification
1.  **Test Create**: `curl -X POST .../users -d '{"name": "Max", "pet_name": "Rocky"}'`
2.  **Test Upload URL**: Call `GET .../upload-url`, receives presigned URL.
3.  **Test Image Upload**: Use `curl -X PUT -T image.jpg "PRESIGNED_URL"`
4.  **Test Profile Update**: Update user with new `avatar_url`.
5.  **Test Get**: Verify `avatar_url` is returned.