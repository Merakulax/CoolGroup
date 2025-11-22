import pytest
import json
import os
from unittest.mock import MagicMock, patch
import sys

# Add lambda paths to sys.path to simulate lambda environment
sys.path.append(os.path.abspath("cloud/lambda/orchestrator"))
sys.path.append(os.path.abspath("cloud/lambda/agents/state_reactor"))
# We might need to patch imports because agents/state_reactor imports 'core' which is local to it
# But orchestrator imports 'boto3'

# --- Test Orchestrator Routing ---
@patch.dict(os.environ, {
    'PROACTIVE_COACH_FUNCTION': 'test-coach-func',
    'STATE_REACTOR_FUNCTION': 'test-reactor-func'
})
@patch('boto3.client')
def test_orchestrator_routing_sensor_data(mock_boto_client):
    import agentic_loop
    
    # Setup Mock
    mock_lambda = MagicMock()
    mock_boto_client.return_value = mock_lambda
    
    # Mock response from child lambda
    mock_response_payload = json.dumps({'status': 'success', 'state': 'HAPPY'})
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=MagicMock(return_value=mock_response_payload.encode('utf-8')))
    }
    
    # Event
    event = {'user_id': 'user123', 'sensor_data': {'hr': 70}}
    
    # Execute
    agentic_loop.lambda_client = mock_lambda # Inject mock directly if client is created at module level
    response = agentic_loop.handler(event, None)
    
    # Verify
    assert response == {'status': 'success', 'state': 'HAPPY'}
    mock_lambda.invoke.assert_called_once()
    call_args = mock_lambda.invoke.call_args
    assert call_args[1]['FunctionName'] == 'test-reactor-func'
    assert json.loads(call_args[1]['Payload']) == event

# --- Test State Reactor Logic (End-to-End Logic with Mocks) ---
@patch('boto3.resource')
@patch('boto3.client')
def test_state_reactor_logic(mock_boto_client, mock_boto_resource):
    # Import handler
    # Since we added 'cloud/lambda/agents/state_reactor' to sys.path, we can import handler
    # But wait, if we just 'import handler', it might conflict if there are multiple handlers?
    # Let's use importlib to be safe or just assume it's the first one found.
    # Better: import handler as reactor_handler
    import handler as reactor_handler
    
    # Mock DynamoDB
    mock_dynamo = MagicMock()
    mock_boto_resource.return_value = mock_dynamo
    mock_table = MagicMock()
    mock_dynamo.Table.return_value = mock_table
    
    # Mock database calls
    # get_last_health_reading
    mock_table.query.return_value = {'Items': [{'heart_rate': 70, 'timestamp': 1234567890}]}
    # get_recent_history
    # get_last_state
    mock_table.get_item.return_value = {'Item': {'stateEnum': 'NEUTRAL', 'timestamp': 1234500000}}
    
    # Mock Context Retriever Lambda (invoked via boto3.client('lambda'))
    mock_lambda = MagicMock()
    mock_boto_client.return_value = mock_lambda # This mocks all clients (lambda, bedrock)
    
    # We need to differentiate clients. 
    # In the code: 
    # lambda_client = boto3.client('lambda') 
    # bedrock_runtime = boto3.client('bedrock-runtime')
    
    def side_effect_client(service_name):
        if service_name == 'lambda':
            l_mock = MagicMock()
            # Mock Context Retriever response
            l_mock.invoke.return_value = {
                'Payload': MagicMock(read=MagicMock(return_value=json.dumps({'context_data': 'User is healthy'}).encode('utf-8')))
            }
            return l_mock
        if service_name == 'bedrock-runtime':
            b_mock = MagicMock()
            # Mock Bedrock Converse response
            b_mock.converse.return_value = {
                'output': {
                    'message': {
                        'content': [
                            {'toolUse': {'input': {'state': 'HAPPY', 'mood': 'Great', 'reasoning': 'Good HR'}} }]
                    }
                }
            }
            return b_mock
        return MagicMock()

    mock_boto_client.side_effect = side_effect_client
    
    # Patch the module-level clients in the imported modules
    with patch('core.database.health_table', mock_table), \
         patch('core.database.user_state_table', mock_table), \
         patch('core.context.lambda_client', side_effect_client('lambda')), \
         patch('core.llm.bedrock_runtime', side_effect_client('bedrock-runtime')):
         
        event = {'user_id': 'user123'}
        response = reactor_handler.handler(event, None)
        
        # Verify
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'UPDATED' # Should update because NEUTRAL -> HAPPY
        assert body['new_state'] == 'HAPPY'
