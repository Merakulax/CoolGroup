from .base_agent import BaseAgent
from datetime import datetime

class VitalsAgent(BaseAgent):
    def analyze(self, history, user_profile):
        data_str = self._format_history(history)
        
        system_prompt = """You are a Cardiologist Agent.
        Your goal is to analyze cardiovascular and physiological metrics to determine the body's load.
        
        Input Data: HR, HRV, Resting HR, SpO2, Body/Skin Temp, Stress Score.
        
        Rules:
        - Ignore movement (that's the Activity Agent's job). Focus purely on internal load.
        - High Temp + High Resting HR -> Suspect Illness/Fever.
        - High HR + Low HRV -> High Physiological Stress (could be exercise or panic).
        - Low HR + High HRV -> Recovery/Rest.
        """
        
        tool_schema = {
            "type": "object",
            "properties": {
                "physiology": {
                    "type": "string",
                    "enum": ["Resting", "Elevated", "Recovery", "Panic", "Fever/Illness"]
                },
                "stress_type": {
                    "type": "string",
                    "enum": ["Acute", "Chronic", "None"]
                },
                "risk_level": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High"]
                },
                "reasoning": {
                    "type": "string"
                }
            },
            "required": ["physiology", "risk_level", "reasoning"]
        }
        
        user_prompt = f"Analyze this recent physiological history:\n{data_str}"
        
        return self.invoke_bedrock(system_prompt, user_prompt, "submit_vitals_analysis", tool_schema)

    def _format_history(self, history):
        formatted = []
        for item in history:
            ts = datetime.fromtimestamp(int(item['timestamp'])/1000).strftime('%H:%M:%S')
            hr = item.get('heartRate', 'N/A')
            hrv = item.get('heartRateVariabilityRMSSD', 'N/A')
            stress = item.get('stressScore', 'N/A')
            temp = item.get('bodyTemperature', 'N/A')
            spo2 = item.get('spo2', 'N/A')
            
            formatted.append(f"[{ts}] HR={hr}, HRV={hrv}, Stress={stress}, Temp={temp}, SpO2={spo2}")
        return "\n".join(formatted)
