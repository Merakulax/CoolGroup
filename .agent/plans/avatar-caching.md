# Execution Plan: Avatar Caching Mechanism

## 1. Objective
Implement a caching mechanism for the `avatar_generator` Lambda to prevent redundant generation of images and videos for identical user states. This will reduce latency and API costs (Google Gemini/Veo).

## 2. Architecture Changes

### Database (DynamoDB)
Create a new DynamoDB table to store the mapping between state hashes and generated asset URLs.
*   **Table Name**: `tamagotchi-avatar-cache-{env}`
*   **Partition Key**: `cache_hash` (String) - SHA256 hash of the generation prompt + base avatar ID.
*   **Attributes**:
    *   `image_url` (String): S3 URL of the generated image.
    *   `video_url` (String): Cloud Storage/S3 URL of the generated video.
    *   `prompt` (String): The text prompt used (for debugging/collisions).
    *   `created_at` (Number): Timestamp.

### Lambda (`avatar_generator`)
Modify the generator logic to:
1.  Construct the prompt based on user state (`mood`, `activity`, etc.).
2.  Compute a deterministic hash: `SHA256(prompt + base_avatar_selection)`.
3.  Query the `avatar_cache` table.
4.  **Cache Hit**: Return stored `image_url` and `video_url` immediately. Update `user_state` table.
5.  **Cache Miss**: Proceed with Gemini/Veo generation. Store new URLs in `avatar_cache`.

## 3. Implementation Steps

### Step 1: Infrastructure (Terraform)
*   **File**: `cloud/infrastructure/terraform/dynamodb.tf`
    *   Add `aws_dynamodb_table` resource for `avatar_cache`.
*   **File**: `cloud/infrastructure/terraform/lambda.tf`
    *   Update `aws_lambda_function.avatar_generator` environment variables to include `AVATAR_CACHE_TABLE`.

### Step 2: Application Logic (Python)
*   **File**: `cloud/lambda/avatar/generator.py`
    *   Import `hashlib`.
    *   Initialize the new DynamoDB table resource.
    *   Implement `get_cached_avatar(hash)` and `cache_avatar(hash, data)` helper functions.
    *   Integrate caching flow into the `handler` function.
    *   Ensure `update_user_state` is still called on cache hits so the frontend receives the update event.

### Step 3: Validation
*   **Unit Test**: Create a test case with the same input state twice.
    *   Run 1: Should trigger generation (mocked).
    *   Run 2: Should return cached result (mocked generation should not be called).
*   **Manual Test**: Trigger state change, observe latency. Repeat state change, observe reduced latency.

## 4. Rollback Plan
If issues arise (e.g., hash collisions, stale cache):
*   Disable the cache read logic in `generator.py` (feature flag or revert code).
*   The system falls back to always generating.
