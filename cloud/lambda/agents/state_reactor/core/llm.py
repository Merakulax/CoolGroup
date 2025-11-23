import os
import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime')
MODEL_ID = os.environ.get('MODEL_ID', 'eu.anthropic.claude-sonnet-4-5-20250929-v1:0')

# --- EXPERT SCHEMAS ---

ACTIVITY_EXPERT_SCHEMA = {
  "toolSpec": {
    "name": "activity_expert_analysis",
    "description": "Analyzes physical activity data to determine user's movement context.",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "activity_type": {
            "type": "string",
            "enum": ["Sleeping", "Sedentary", "Walking", "Running", "Cycling", "Commuting", "Workout", "Unknown"],
            "description": "The classified physical activity."
          },
          "intensity": {
            "type": "string",
            "enum": ["Low", "Moderate", "High"],
            "description": "Intensity of the activity."
          },
          "reasoning": {
            "type": "string",
            "description": "Explanation based on accelerometer, speed, and step data."
          }
        },
        "required": ["activity_type", "intensity", "reasoning"]
      }
    }
  }
}

VITALS_EXPERT_SCHEMA = {
  "toolSpec": {
    "name": "vitals_expert_analysis",
    "description": "Analyzes physiological vitals to determine health safety and status.",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "status": {
            "type": "string",
            "enum": ["Normal", "Elevated", "Critical", "Recovery", "Abnormal"],
            "description": "The physiological status."
          },
          "potential_issues": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Potential detected issues (e.g., 'Fever', 'Tachycardia', 'Low SpO2')."
          },
          "reasoning": {
            "type": "string",
            "description": "Explanation based on HR, Temp, SpO2."
          }
        },
        "required": ["status", "reasoning"]
      }
    }
  }
}

WELLBEING_EXPERT_SCHEMA = {
  "toolSpec": {
    "name": "wellbeing_expert_analysis",
    "description": "Analyzes sleep, stress, and mood to determine mental wellbeing.",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "mental_state": {
            "type": "string",
            "enum": ["Calm", "Stressed", "Anxious", "Exhausted", "Energetic"],
            "description": "The inferred mental state."
          },
          "recovery_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Estimated recovery level (0-100)."
          },
          "reasoning": {
            "type": "string",
            "description": "Explanation based on HRV, Stress Score, Sleep."
          }
        },
        "required": ["mental_state", "reasoning"]
      }
    }
  }
}

# --- SUPERVISOR SCHEMA ---

SUPERVISOR_SCHEMA = {
  "toolSpec": {
    "name": "pet_state_supervisor_decision",
    "description": "Synthesizes expert inputs to determine the final Pet State.",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "state": {
            "type": "string",
            "enum": ["HAPPY", "TIRED", "STRESS", "SICKNESS", "EXERCISE", "ANXIOUS", "NEUTRAL"],
            "description": "The final emotional and physiological state of the pet."
          },
          "mood": {
            "type": "string",
            "description": "A brief, descriptive word for the pet's mood."
          },
          "reasoning": {
            "type": "string",
            "description": "A SINGLE sentence explaining the determined state."
          },
          "activity": {
            "type": "string",
            "enum": ["Sleeping", "Coding", "Running", "Commuting", "Resting", "Meditating", "Unknown", "Working", "Walking", "Cycling"],
            "description": "The final agreed-upon activity context."
          }
        },
        "required": ["state", "mood", "reasoning", "activity"]
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
