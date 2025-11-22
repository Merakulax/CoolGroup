import json
from core import database, llm
from core.utils import DecimalEncoder
from core.llm import INTERVENTION_TOOL_SCHEMA

def run():
    """
    Iterates through active users and runs the Coach Model for each.
    """
    print("Starting Proactive Coach Loop")

    # Get all users
    users = database.get_all_users()
    print(f"Running Coach for {len(users)} users.")
    
    results = []
    
    for user in users:
        user_id = user.get('user_id')
        if not user_id:
            continue

        print(f"Coaching User: {user_id}")
        
        history = database.get_recent_history(user_id, limit=20)
        summary_str = json.dumps(history, cls=DecimalEncoder)
        
        # Extract user profile data for persona injection
        motivation_style = user.get('motivation_style', 'Proactive')
        goals = ', '.join(user.get('goals', ['overall health']))
        preferred_tone = user.get('preferred_tone', 'supportive')
        
        system_prompt = f"""You are a {motivation_style} Health Coach for a Tamagotchi-like health companion.
Your goal is to analyze the user's daily summary and decide if an intervention is needed.
The user's primary health goals include: {goals}.
When providing advice or interventions, use a {preferred_tone} tone.

Based on the daily summary, call the 'proactive_coach_intervention' tool to recommend an intervention or indicate none is needed.
"""

        user_message = f"""
        Daily Summary for {user_id}:
        {summary_str}
        
        Analyze this summary and suggest an intervention if needed.
        """
        try:
            analysis = llm.invoke_model_structured(system_prompt, user_message, INTERVENTION_TOOL_SCHEMA, temperature=0.7)
            
            if analysis and analysis.get('intervention') != 'NONE':
                # TODO: Implement actual push notification
                print(f"Intervention Suggested for {user_id}: {analysis['intervention']} - {analysis['reasoning']}")
                results.append({
                    'user': user_id,
                    'intervention': analysis['intervention'],
                    'reasoning': analysis['reasoning']
                })
                
        except Exception as e:
            print(f"Failed to coach user {user_id}: {e}")
            
    return {'statusCode': 200, 'body': json.dumps({'results': results}, cls=DecimalEncoder)}