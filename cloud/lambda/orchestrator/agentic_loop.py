"""
Agentic Loop Orchestrator
Coordinates the Perception → Reasoning → Planning → Action cycle
"""

import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

# Clients
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')

# Tables
user_state_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'user_state'))
health_table = dynamodb.Table(os.environ.get('HEALTH_TABLE', 'health_data'))

def handler(event, context):
    """
    Orchestrate the agentic AI loop
    """
    try:
        user_id = event.get('user_id')
        analysis = event.get('analysis', {})
        
        # Check for demo trigger overrides
        force_state = event.get('force_state')
        custom_message = event.get('custom_message')

        print(f"Starting agentic loop for user {user_id}")

        # 1. PERCEPTION: Gather full context
        # For MVP, we use the latest sensor reading in analysis OR fetch from DB
        health_context = gather_context(user_id, analysis)
        print(f"Health Context: {health_context}")

        # 2. LOGIC: Determine State (1-10)
        if force_state:
            state_index = int(force_state)
            mood = "Forced State"
            reasoning = "Demo Override"
        else:
            state_index, mood, reasoning = calculate_state_logic(health_context)
        
        print(f"Determined State: {state_index} ({mood})")

        # 3. NARRATIVE: Generate AI Message
        if custom_message:
            message = custom_message
        else:
            message = generate_message(state_index, mood, health_context)
        
        print(f"AI Message: {message}")

        # 4. PERSISTENCE: Update Pet State
        new_state = {
            'user_id': user_id,
            'stateIndex': state_index,
            'mood': mood,
            'energy': calculate_energy(health_context),
            'message': message,
            'internalReasoning': reasoning,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'last_updated': datetime.now().isoformat()
        }
        
        update_pet_state(new_state)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'user_id': user_id,
                'new_state': new_state,
                'success': True
            }, default=str)
        }

    except Exception as e:
        print(f"Error in agentic loop: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def gather_context(user_id, analysis):
    """
    Gather health context from analysis payload or recent DB records
    """
    # If analysis has the data (from ingest), use it.
    # Otherwise, we might query DDB (omitted for speed in MVP)
    
    # Default values
    context = {
        'sleep_score': analysis.get('sleep_score', 70),
        'recovery_score': analysis.get('recovery_score', 70),
        'stress_level': analysis.get('stress_level', 30),
        'avg_hr': analysis.get('avg_heart_rate', 70)
    }
    return context

def calculate_state_logic(context):
    """
    Map physiological data to 1-10 state.
    Returns: (state_index, mood_string, reasoning)
    """
    sleep = context.get('sleep_score', 0)
    recovery = context.get('recovery_score', 0)
    stress = context.get('stress_level', 0)
    
    # Simple Algorithm
    # Base score: Average of Sleep + Recovery
    base = (sleep + recovery) / 2
    
    # Penalize for stress
    if stress > 70:
        base -= 20
    
    # Normalize to 1-10
    score = max(1, min(10, int(base / 10)))
    
    # Mood Mapping
    moods = {
        1: "Exhausted", 2: "Sick", 3: "Tired", 4: "Concerned", 
        5: "Okay", 6: "Recovering", 7: "Good", 8: "Energetic", 
        9: "Happy", 10: "Ecstatic"
    }
    
    reasoning = f"Sleep={sleep}, Recovery={recovery}, Stress={stress} -> Base={base}"
    return score, moods.get(score, "Neutral"), reasoning

def calculate_energy(context):
    """Calculate 'Energy Budget' (Spoons) 0-100"""
    return int((context.get('sleep_score', 50) + context.get('recovery_score', 50)) / 2)

def generate_message(state_index, mood, context):
    """
    Use Bedrock (Claude) to generate the German persona message
    """
    try:
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        system_prompt = """Du bist ein Tamagotchi Health Companion. 
        Deine Aufgabe ist es, deinen Zustand basierend auf den Gesundheitsdaten des Nutzers zu verkörpern.
        Sprich immer in der Ich-Perspektive. 
        Halte dich kurz (max 1-2 Sätze).
        Sei empathisch aber ehrlich."""
        
        user_prompt = f"""
        Aktueller Status:
        - Level: {state_index}/10
        - Stimmung: {mood}
        - Schlaf: {context.get('sleep_score')}/100
        - Erholung: {context.get('recovery_score')}/100
        
        Generiere eine Nachricht an den Nutzer auf Deutsch."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        })

        response = bedrock_runtime.invoke_model(
            body=body, 
            modelId=model_id, 
            accept='application/json', 
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']

    except Exception as e:
        print(f"Bedrock error: {e}")
        return f"Ich fühle mich {mood}. (AI Offline)"

def update_pet_state(state_item):
    """Update user_state table"""
    # Convert float/int to Decimal is standard for Boto3 DDB, 
    # but simple types usually work. If issues arise, explicit Decimal conversion needed.
    user_state_table.put_item(Item=state_item)
