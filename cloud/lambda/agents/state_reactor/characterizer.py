import json
import os
from core import llm
from core.utils import DecimalEncoder

CHARACTERIZER_SCHEMA = {
    "toolSpec": {
        "name": "generate_character_message",
        "description": "Generates a first-person message from the pet to the user.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The character-driven message to the user."}
                },
                "required": ["message"]
            }
        }
    }
}

def handler(event, context):
    print(f"Characterizer Received: {json.dumps(event)}")
    
    analysis = event.get('analysis', {})
    user_profile = event.get('user_profile', {})
    
    # Extract context
    state = analysis.get('state', 'UNKNOWN')
    reasoning = analysis.get('reasoning', 'No reasoning provided.')
    
    user_name = user_profile.get('name', 'User')
    pet_name = user_profile.get('pet_name', 'Your Pet')
    goals = user_profile.get('goals', [])
    motivation_style = user_profile.get('motivation_style', 'supportive')
    
    prompt = f"""You are {pet_name}, a virtual health companion.
    
Your Personality:
- Name: {pet_name}
- Role: Health Coach & Companion
- Style: {motivation_style} (e.g., if 'STRICT', be firm; if 'ENCOURAGING', be gentle).

User Context:
- Name: {user_name}
- Current State: {state}
- Goals: {', '.join(goals)}

Technical Reasoning for State:
"{reasoning}"

Task:
Rewrite the technical reasoning into a SINGLE, natural, first-person sentence.

PERSPECTIVE RULES:
1. ALWAYS speak in the FIRST PERSON ("I", "Me", "My").
   - The Pet MIRRORS the User's data as its own feelings.
   - This applies to ALL states, INCLUDING STRESS.
   - Do NOT say "You seem overwhelmed."
   - SAY "I feel overwhelmed, let's take a breath."
   - Do NOT say "You walked 10k steps".
   - SAY "I feel so energetic after our walk!"

Constraints:
- Be concise (max 15 words).
- Match the {motivation_style} tone.
"""

    result = llm.invoke_model_structured(prompt, "Generate Character Message", CHARACTERIZER_SCHEMA, temperature=0.7)
    
    if not result:
        # Fallback
        return {'message': f"I think you are in {state} state."}
        
    return result
