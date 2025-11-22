import os
import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime')
MODEL_ID = os.environ.get('MODEL_ID', 'eu.anthropic.claude-sonnet-4-5-20250929-v1:0')

# --- JSON Schemas for Structured Output ---
PET_STATE_TOOL_SCHEMA = {
  "toolSpec": {
    "name": "pet_state_analyzer",
    "description": "Analyzes health data and determines the pet's current emotional and physiological state.",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "state": {
            "type": "string",
            "enum": ["HAPPY", "TIRED", "STRESS", "SICKNESS", "EXERCISE", "ANXIOUS", "NEUTRAL"],
            "description": "The current emotional and physiological state of the pet."
          },
          "mood": {
            "type": "string",
            "description": "A brief, descriptive word for the pet's mood (e.g., 'Energized', 'Restless')."
          },
          "reasoning": {
            "type": "string",
            "description": "A concise, user-friendly explanation for the determined state, based on health data."
          }
        },
        "required": ["state", "mood", "reasoning"]
      }
    }
  }
}

INTERVENTION_TOOL_SCHEMA = {
  "toolSpec": {
    "name": "proactive_coach_intervention",
    "description": "Analyzes user trends and suggests a proactive health intervention if needed.",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "intervention": {
            "type": "string",
            "enum": ["STRESS_RELIEF", "MOTIVATION", "NONE"],
            "description": "Recommended intervention type based on trend analysis. 'NONE' if no intervention is needed."
          },
          "reasoning": {
            "type": "string",
            "description": "A concise explanation for the recommended intervention or why none is needed."
          }
        },
        "required": ["intervention", "reasoning"]
      }
    }
  }
}

def invoke_model_structured(system_prompt, user_message, tool_schema, temperature=0.5):
    """
    Invokes the Bedrock model using the Converse API with tool use for structured output.
    """
    print(f"Invoking Model: {MODEL_ID} with tool {tool_schema['toolSpec']['name']}")
    try:
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            system=[{"text": system_prompt}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ],
            toolConfig={
                "tools": [tool_schema],
                "toolChoice": {"tool": {"name": tool_schema['toolSpec']['name']}}
            },
            inferenceConfig={
                "temperature": temperature,
                "maxTokens": 500
            }
        )
        
        output_content = response['output']['message']['content']
        
        # Extract tool use from the response
        for content_block in output_content:
            if 'toolUse' in content_block:
                return content_block['toolUse']['input']
        
        print(f"Warning: No tool use found in model response: {output_content}")
        return None

    except Exception as e:
        print(f"Bedrock Structured Invocation Error: {e}")
        return None