import json
from boto3 import client as boto3_client

lambda_client = boto3_client('lambda')

# Method to send a Slack notification
def send_slack_notification(message, channel_name):
    payload = {
        "channel": channel_name,  # as per the usecase defined
        "text": message,
    }

    response = requests.post(slack_webhook_url, json=payload)

    if response.status_code == 200:
        print("Slack notification sent successfully.")
        return {
        'statusCode': response.status_code,
        'body': json.dumps("Slack notification sent successfully.")
        }
    else:
        print(f"Failed to send Slack notification with status code: {response.status_code}")
        return {
        'statusCode': response.status_code,
        'body': json.dumps(f"Failed to send Slack notification with status code: {response.status_code}")
        }

def lambda_handler(event, context):
    responsePayload = send_slack_notification(event.get("message"), event.get("channel_name"))
    return responsePayload

