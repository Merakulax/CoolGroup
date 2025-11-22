import json

def handler(event, context):
    print("Event:", json.dumps(event))
    body = event.get('body', '')
    
    # If body is JSON string, try to parse it to return structured data, or just return as is
    try:
        parsed_body = json.loads(body)
        response_body = json.dumps({
            "message": "Echo",
            "received": parsed_body
        })
    except:
        response_body = body

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': response_body
    }
