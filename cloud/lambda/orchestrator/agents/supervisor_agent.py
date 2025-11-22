from .base_agent import BaseAgent
import json

class SupervisorAgent(BaseAgent):
    def analyze(self, activity_result, vitals_result, wellbeing_result, user_profile):
        
        system_prompt = """You are the Head Health Coach (Supervisor).
        Your goal is to synthesize reports from your team of experts to determine the final User State and Pet Mood.
        
        Inputs:
        1. Activity Agent: Context (Sedentary/Running), Environment.
        2. Vitals Agent: Physiology (Resting/Elevated/Fever).
        3. Wellbeing Agent: Mental State (Burnout/Balanced).
        
        Logic Guidelines:
        - IF Activity='Not Worn' -> State='UNKNOWN'.
        - IF Activity='Sedentary' AND Vitals='Elevated' -> State='STRESS' (Anxiety) OR 'SICKNESS' (if Fever).
        - IF Activity='Running' AND Vitals='Elevated' -> State='EXERCISE'.
        - IF Activity='Sedentary' AND Vitals='Resting' AND Wellbeing='Burnout Risk' -> State='RECOVERY_NEEDED'.
        - IF Activity='Hiking' -> State='EXERCISE' (Nature context).
        """
        
        tool_schema = {
            "type": "object",
            "properties": {
                "state": {
                    "type": "string",
                    "enum": ["REST", "WORK", "EXERCISE", "STRESS", "SLEEP", "SICKNESS", "UNKNOWN", "RECOVERY_NEEDED"]
                },
                "mood": {
                    "type": "string",
                    "description": "Pet Mood Adjective (e.g., Worried, Energetic, Sleeping, Excited)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Final synthesis of why this state was chosen."
                }
            },
            "required": ["state", "mood", "reasoning"]
        }
        
        user_prompt = f"""
        Expert Reports:
        
        [ACTIVITY AGENT]
        {json.dumps(activity_result)}
        
        [VITALS AGENT]
        {json.dumps(vitals_result)}
        
        [WELLBEING AGENT]
        {json.dumps(wellbeing_result)}
        
        Determine the final state.
        """
        
        return self.invoke_bedrock(system_prompt, user_prompt, "submit_final_decision", tool_schema)

    # Supervisor doesn't use the standard 'analyze(history)' signature
    # It uses the specialized signature above.
