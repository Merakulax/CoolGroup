import sys
import os
import json
import pytest
import importlib.util
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Helper to load modules from paths with isolation
def load_handler_isolated(handler_path, module_name, core_parent_path):
    """
    Loads a handler module while ensuring its local 'core' package is prioritized.
    Unloads any existing 'core' from sys.modules to prevent cross-contamination.
    """
    # 1. Unload 'core' and its submodules
    for key in list(sys.modules.keys()):
        if key == 'core' or key.startswith('core.'):
            del sys.modules[key]

    # 2. Prepend the correct parent path to sys.path
    sys.path.insert(0, core_parent_path)
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, handler_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        # 3. Cleanup sys.path
        if sys.path[0] == core_parent_path:
            sys.path.pop(0)

# Paths
reactor_dir = os.path.abspath("cloud/lambda/agents/state_reactor")
coach_dir = os.path.abspath("cloud/lambda/agents/proactive_coach")
ingest_dir = os.path.abspath("cloud/lambda/ingest")

reactor_path = os.path.join(reactor_dir, "handler.py")
coach_path = os.path.join(coach_dir, "handler.py")
ingest_path = os.path.join(ingest_dir, "sensor_ingest.py")

# --- Mock Data Helpers ---

def create_mock_sensor_data(scenario):
    if scenario == "stress":
        return {
            "heartRate": 120,
            "accelerometer": {"x": 0.01, "y": 0.02, "z": 0.98},
            "timestamp": 1600000000000
        }
    elif scenario == "workout":
        return {
            "heartRate": 150,
            "accelerometer": {"x": 1.2, "y": 0.8, "z": 0.5},
            "timestamp": 1600000000000
        }
    elif scenario == "sleep":
        return {
            "heartRate": 55,
            "sleep_status": "ASLEEP",
            "timestamp": 1600000000000
        }
    return {}

# --- Test Cases ---

@patch('boto3.resource')
@patch('boto3.client')
def test_state_reactor_scenarios(mock_boto_client, mock_boto_resource):
    """
    Tests the State Reactor's response to different sensor data scenarios (Stress, Workout).
    """
    # Load with isolation
    reactor = load_handler_isolated(reactor_path, "state_reactor_handler", reactor_dir)
    
    # Setup Mocks
    mock_table = MagicMock()
    mock_dynamo = MagicMock()
    mock_dynamo.Table.return_value = mock_table
    mock_boto_resource.return_value = mock_dynamo
    
    def side_effect_client(service_name, **kwargs):
        mock = MagicMock()
        if service_name == 'bedrock-runtime':
            def converse_side_effect(**kwargs):
                messages = kwargs.get('messages', [])
                user_text = messages[0]['content'][0]['text']
                
                state = "NEUTRAL"
                mood = "Okay"
                reasoning = "Normal"
                
                if "120" in user_text and "0.01" in user_text: 
                    state = "STRESS"
                    mood = "Anxious"
                    reasoning = "High HR, Low Motion"
                elif "150" in user_text and "1.2" in user_text:
                    state = "EXERCISE"
                    mood = "Energetic"
                    reasoning = "High HR, High Motion"
                elif "55" in user_text:
                    state = "TIRED"
                    mood = "Sleepy"
                    reasoning = "Low HR"

                return {
                    'output': {
                        'message': {
                            'content': [{
                                'toolUse': {
                                    'input': {'state': state, 'mood': mood, 'reasoning': reasoning},
                                    'name': 'pet_state_analyzer',
                                    'toolUseId': 'tool_1'
                                }
                            }]
                        }
                    }
                }
            mock.converse.side_effect = converse_side_effect
        return mock

    mock_boto_client.side_effect = side_effect_client

    scenarios = ["stress", "workout", "sleep"]
    
    # We patch 'core.database' which should now be the one from state_reactor
    with patch('core.database.health_table', mock_table), \
         patch('core.database.user_state_table', mock_table), \
         patch('core.llm.bedrock_runtime', side_effect_client('bedrock-runtime')), \
         patch('core.context.lambda_client', MagicMock()):

        for scenario in scenarios:
            print(f"Testing Scenario: {scenario}")
            data = create_mock_sensor_data(scenario)
            mock_table.query.return_value = {'Items': [data]} 
            mock_table.get_item.return_value = {}
            
            event = {'user_id': 'test_user'}
            response = reactor.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            
            expected_state = {"stress": "STRESS", "workout": "EXERCISE", "sleep": "TIRED"}[scenario]
            assert body['new_state'] == expected_state
            assert body['status'] == 'UPDATED'


@patch('boto3.resource')
@patch('boto3.client')
def test_proactive_coach_personas(mock_boto_client, mock_boto_resource):
    """
    Tests that the Proactive Coach picks up the User Profile (Persona).
    """
    # Load with isolation (clears previous core)
    coach = load_handler_isolated(coach_path, "proactive_coach_handler", coach_dir)
    
    mock_table = MagicMock()
    mock_dynamo = MagicMock()
    mock_dynamo.Table.return_value = mock_table
    mock_boto_resource.return_value = mock_dynamo

    # Mock Users Table to return specific Personas
    # Note: The database.py code has a hardcoded 'enrichment' step that maps user123/user456/user789 to specific profiles.
    # We must use these IDs to ensure the 'STRICT' profile is applied correctly, otherwise it defaults to user123 (Encouraging).
    users_db_data = [
        {'user_id': 'user456', 'motivation_style': 'STRICT', 'preferred_tone': 'direct'},
        {'user_id': 'user123', 'motivation_style': 'ENCOURAGING', 'preferred_tone': 'supportive'}
    ]
    
    # Important: Override the scan return value on the table instance that core.database uses
    mock_table.scan.return_value = {'Items': users_db_data}
    mock_table.query.return_value = {'Items': []} 
    
    mock_bedrock = MagicMock()
    mock_boto_client.return_value = mock_bedrock
    
    def converse_side_effect(**kwargs):
        return {
            'output': {
                'message': {
                    'content': [{
                        'toolUse': {
                            'input': {'intervention': 'NONE', 'reasoning': 'Test'},
                            'name': 'proactive_coach_intervention',
                            'toolUseId': '1'
                        }
                    }]
                }
            }
        }
    
    mock_bedrock.converse.side_effect = converse_side_effect

    # Patch the FRESHLY LOADED core
    with patch('core.database.users_table', mock_table), \
         patch('core.database.health_table', mock_table), \
         patch('core.llm.bedrock_runtime', mock_bedrock):
        
        coach.handler({}, None)
        
        assert mock_bedrock.converse.call_count >= 2
        calls = mock_bedrock.converse.call_args_list
        prompts = [c[1]['system'][0]['text'] for c in calls]
        
        has_strict = any("STRICT" in p for p in prompts)
        has_kind = any("ENCOURAGING" in p for p in prompts)
        
        assert has_strict, f"Strict persona not found. Prompts: {prompts}"
        assert has_kind, "Encouraging persona not found"


@patch('boto3.resource')
@patch('boto3.client')
def test_environment_simulator_fever(mock_boto_client, mock_boto_resource):
    """
    Tests if the Ingest Lambda correctly processes the complex Environment Simulator payload.
    """
    # Ingest doesn't have 'core' but we can use the helper to set path
    ingest = load_handler_isolated(ingest_path, "ingest_handler", ingest_dir)
    
    mock_table = MagicMock()
    mock_dynamo = MagicMock()
    mock_dynamo.Table.return_value = mock_table
    mock_boto_resource.return_value = mock_dynamo
    mock_lambda_client = MagicMock()
    mock_boto_client.return_value = mock_lambda_client

    payload = {
        "user_id": "sick_user",
        "batch": [
            {
                "timestamp": 123456,
                "heartRate": 90,
                "body_temp": 38.5,
                "raw_complex": {"vitals": {"bodyTemperature": 38.5}}
            }
        ]
    }
    
    event = {'body': json.dumps(payload)}
    
    # Patch directly on the loaded module
    with patch.object(ingest, 'health_table', mock_table), \
         patch.object(ingest, 'lambda_client', mock_lambda_client):
        
        response = ingest.handler(event, None)
        
        assert response['statusCode'] == 200
        mock_table.batch_writer.assert_called()
        mock_lambda_client.invoke.assert_called_once()

