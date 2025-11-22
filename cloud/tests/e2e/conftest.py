import pytest
import os
import boto3
import requests
from botocore.config import Config

# Constants
DEFAULT_REGION = "eu-central-1"

def pytest_addoption(parser):
    parser.addoption("--api-url", action="store", help="Base URL of the deployed API Gateway")
    parser.addoption("--stack-name", action="store", default="tamagotchi-health-dev", help="CloudFormation stack name")

@pytest.fixture(scope="session")
def api_url(request):
    url = request.config.getoption("--api-url")
    if not url:
        # Try to fetch from CloudFormation if not provided
        stack_name = request.config.getoption("--stack-name")
        try:
            cf = boto3.client('cloudformation', region_name=DEFAULT_REGION)
            response = cf.describe_stacks(StackName=stack_name)
            outputs = response['Stacks'][0]['Outputs']
            for out in outputs:
                if out['OutputKey'] == 'api_endpoint':
                    url = out['OutputValue']
                    break
        except Exception as e:
            print(f"Warning: Could not auto-discover API URL: {e}")
    
    if not url:
        # Fallback to env var or fail
        url = os.environ.get("API_URL")
    
    if not url:
        pytest.skip("API URL not provided. Use --api-url or set API_URL env var.")
    
    return url.rstrip('/')

@pytest.fixture(scope="session")
def aws_region():
    return os.environ.get("AWS_REGION", DEFAULT_REGION)

@pytest.fixture(scope="session")
def dynamodb_table(request):
    table = os.environ.get("DYNAMODB_TABLE")
    if not table:
        # Try auto-discover
        stack_name = request.config.getoption("--stack-name")
        try:
            cf = boto3.client('cloudformation', region_name=DEFAULT_REGION)
            response = cf.describe_stacks(StackName=stack_name)
            outputs = response['Stacks'][0]['Outputs']
            for out in outputs:
                if out['OutputKey'] == 'dynamodb_table_name':
                    table = out['OutputValue']
                    break
        except:
            pass
            
    if not table:
        pytest.skip("DynamoDB Table not found.")
        
    return table

@pytest.fixture(scope="session")
def http_session():
    return requests.Session()

@pytest.fixture(scope="session")
def db_resource(aws_region):
    return boto3.resource('dynamodb', region_name=aws_region)
