from .base_agent import BaseAgent
from datetime import datetime

class WellbeingAgent(BaseAgent):
    def analyze(self, history, user_profile):
        # Wellbeing might need broader context, but we'll work with the stream for now
        # Ideally, we'd fetch "Last Night's Sleep" separately. 
        # For this MVP, we assume sleep data comes in as a periodic update or we look at "Time of Day".
        
        data_str = self._format_history(history)
        
        system_prompt = """You are a Psychologist/Wellbeing Agent.
        Your goal is to analyze Sleep Architecture, Circadian Rhythms (Light), and Emotional trends.
        
        Input Data: Sleep Stages, Emotion Status, Light Exposure, HRV trends.
        
        Rules:
        - Analyze Sleep Debt: Low Deep/REM sleep -> Burnout Risk.
        - Analyze Circadian: Bright light at night -> Bad sleep hygiene.
        - Analyze Mood: Consistently 'Unpleasant' emotion logs -> Depressed/Anxious state.
        """
        
        tool_schema = {
            "type": "object",
            "properties": {
                "mental_state": {
                    "type": "string",
                    "enum": ["Balanced", "Burnout Risk", "Anxious", "Depressed", "Well-Rested"]
                },
                "sleep_quality": {
                    "type": "string",
                    "enum": ["Good", "Poor", "N/A"]
                },
                "social_battery": {
                    "type": "string",
                    "enum": ["High", "Low"]
                },
                "reasoning": {
                    "type": "string"
                }
            },
            "required": ["mental_state", "reasoning"]
        }
        
        user_prompt = f"Analyze this wellbeing context:\n{data_str}"
        
        return self.invoke_bedrock(system_prompt, user_prompt, "submit_wellbeing_analysis", tool_schema)

    def _format_history(self, history):
        formatted = []
        for item in history:
            ts = datetime.fromtimestamp(int(item['timestamp'])/1000).strftime('%H:%M:%S')
            # Sleep data might appear as a specific record type
            if 'sleepScore' in item:
                sleep = f"Score={item['sleepScore']}, Deep={item.get('deepDuration',0)}"
            else:
                sleep = "No Sleep Data"
                
            emotion = item.get('emotionStatus', 'N/A')
            light = item.get('ambient_light', 'N/A')
            
            formatted.append(f"[ts] Sleep={sleep}, Emotion={emotion}, Light={light}")
        return "\n".join(formatted)
