# ExecPlan: Looping Avatar Video Generation with Veo 3 on Vertex AI

**Status**: Draft
**Date**: 2025-11-23
**Objective**: Generate seamless looping videos of avatars performing health-related actions (e.g., breathing, exercising) using Google's Veo model on Vertex AI.

## 1. Overview
To create a "living" virtual pet, we need animations that loop seamlessly. Instead of manually animating 3D models, we will use **Google Veo (Vertex AI)** to generate video assets where the start and end frames are identical, ensuring a perfect loop.

## 2. Technical Strategy

### 2.1 Model & API
    - **Model**: `veo-3.1-generate-001` (or `veo-3.0` if available/preview).- **API**: Vertex AI Video Generation API via `google-genai` Python SDK.
- **Key Feature**: **First and Last Frame Specification**.
    - By setting `first_frame` == `last_frame`, we force the model to interpolate an action that starts and returns to the exact same state.

### 2.2 Workflow
1.  **Input**:
    - **Base Image**: A high-quality image of the avatar in a "neutral" or "start" pose.
    - **Prompt**: Description of the action (e.g., "A cute robot doing jumping jacks, keeping the same style").
2.  **Generation**:
    - Call Vertex AI API with:
        - `prompt`: Action description.
        - `first_frame`: Base Image.
        - `last_frame`: Base Image.
        - `duration`: 4s or 8s (depending on action speed).
3.  **Post-Processing** (Optional):
    - If the raw output has minor jitters at the loop point, use `ffmpeg` to cross-fade the last 0.5s with the first 0.5s, though the API constraint should minimize this.
    - Convert to format suitable for Watch (e.g., sequences of PNGs or optimized GIF/MP4).

## 3. Implementation Plan

### 3.1 Setup
- **Location**: `cloud/tools/avatar_generator/`
- **Dependencies**: `google-genai`, `Pillow` (for image handling).
- **Auth**: Standard Google Cloud Application Default Credentials.

### 3.2 Script Structure (`generate_loops.py`)
```python
import os
from google import genai
from google.genai.types import GenerateVideosConfig

def generate_loop(avatar_image_path, prompt, output_path):
    client = genai.Client()
    
    with open(avatar_image_path, "rb") as f:
        image_bytes = f.read()
        
    # Define the loop constraint: Start = End
    response = client.models.generate_video(
        model="veo-2.0-generate-001", # Check for veo-3 availability
        prompt=prompt,
        config=GenerateVideosConfig(
            first_frame=image_bytes, # Start State
            last_frame=image_bytes,  # End State (Forces Loop)
            duration_seconds=4,
            aspect_ratio="1:1"       # Watch face friendly
        )
    )
    
    # Save result
    # Note: Response handling depends on whether it's long-running or sync
    # Usually returns a GCS URI or bytes.
```

### 3.3 Action List
We will generate loops for:
1.  **Idle**: Gentle breathing / hovering.
2.  **Happy**: Cheering / jumping.
3.  **Stressed**: Shaking / glitching.
4.  **Exercise**: Jumping jacks / stretching.
5.  **Sleeping**: Zzz animation.

## 4. Requirements & Dependencies
- GCP Project with "Vertex AI API" enabled.
- Quota for Video Generation API.
- `google-genai` Python package.

## 5. Next Steps
1.  [ ] Create `cloud/tools/avatar_generator/` directory.
2.  [ ] Implement `generate_loops.py` prototype.
3.  [ ] Test with a placeholder avatar image.
4.  [ ] Verify loop smoothness.
