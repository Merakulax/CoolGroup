import json
import boto3
import os

class BaseAgent:
    def __init__(self, model_id="anthropic.claude-sonnet-4-5-20250929-v1:0"):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')
        self.model_id = model_id

    def invoke_bedrock(self, system_prompt, user_prompt, tool_name, tool_schema):
        """
        Invoke Bedrock using the "Tool Use" API to enforce structured output.
        """
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "tools": [{
                "name": tool_name,
                "description": f"Submit the analysis report for {tool_name}.",
                "input_schema": tool_schema
            }],
            "tool_choice": {"type": "tool", "name": tool_name}
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body, 
                modelId=self.model_id, 
                accept='application/json', 
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            
            # Parse Tool Use Response
            content_blocks = response_body.get('content', [])
            for block in content_blocks:
                if block.get('type') == 'tool_use':
                    return block.get('input')
            
            # Fallback if no tool used (unlikely with tool_choice forced)
            print(f"Warning: No tool use block found in response: {response_body}")
            return {"error": "No structured output returned"}

        except Exception as e:
            print(f"Bedrock Error in {self.__class__.__name__}: {e}")
            return {"error": str(e)}

    def analyze(self, data, user_profile):
        """
        To be implemented by subclasses
        """
        raise NotImplementedError
