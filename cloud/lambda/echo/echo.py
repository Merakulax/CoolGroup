import json


def handler(event, context):
    print("Event:", json.dumps(event))
    body = event.get("body", "")

    sample_image_url = "https://picsum.photos/200/300"  # Using a generic placeholder

    response_payload = {"message": "Echo", "image_url": sample_image_url}

    try:
        parsed_body = json.loads(body)
        response_payload["received"] = parsed_body
    except json.JSONDecodeError:
        response_payload["received_raw"] = (
            body  # If not valid JSON, put it as raw string
        )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_payload),
    }

