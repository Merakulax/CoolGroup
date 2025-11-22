from .base_agent import BaseAgent
from datetime import datetime

class ActivityAgent(BaseAgent):
    def analyze(self, history, user_profile):
        # 1. Format Data
        data_str = self._format_history(history)
        
                # 2. Construct Prompt
                system_prompt = """You are a Biomechanics Expert Agent. 
                Your goal is to analyze movement patterns, Elevation, Light, and Wear status to determine the user's Activity Context.
        
                Input Data includes: Steps, Calories, Distance, Intensity, GPS, Barometer (Elevation), Ambient Light, Wear Detection.
                
                Rules:
                - Check WEAR_DETECTION first. If not worn, context is 'Not Worn'.
                - Analyze Barometer/GPS for elevation changes (Hiking/Climbing).
                - Analyze Light: Dark + Sedentary = Sleep/Movie? Bright + Active = Outdoor Sport?
                - Analyze Running Form if available (Impact, Oscillation).
                """
                
                tool_schema = {
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "enum": ["Sedentary", "Walking", "Running", "Commuting", "Hiking", "Not Worn"]
                        },
                        "environment": {
                            "type": "string",
                            "enum": ["Indoor", "Outdoor", "Unknown"]
                        },
                        "form_analysis": {
                            "type": "string", 
                            "description": "Analysis of running efficiency (Efficient/Sloppy) or N/A"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence score between 0.0 and 1.0"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation of the conclusion"
                        }
                    },
                    "required": ["context", "environment", "reasoning"]
                }
        
                user_prompt = f"Analyze this recent activity history:\n{data_str}"
                
                return self.invoke_bedrock(system_prompt, user_prompt, "submit_activity_analysis", tool_schema)
    def _format_history(self, history):
        # Extract relevant fields
        formatted = []
        for item in history:
            ts = datetime.fromtimestamp(int(item['timestamp'])/1000).strftime('%H:%M:%S')
            steps = item.get('stepCount', 0)
            speed = item.get('speed', 0)
            # Mocking new sensor fields if they don't exist in legacy data yet
            wear = item.get('wear_detection', 'WORN') 
            light = item.get('ambient_light', 'N/A')
            barometer = item.get('barometer_hpa', 'N/A')
            
            formatted.append(f"[{ts}] Steps={steps}, Speed={speed}, Wear={wear}, Light={light}, Baro={barometer}")
        return "\n".join(formatted)
