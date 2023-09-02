import json

from boto3 import client as boto3_client
import json

lambda_client = boto3_client('lambda')

# Method to create a ServiceNow incident
def create_servicenow_incident(message, assignment_group):
    payload = {
        "short_description": "Tableau Data Source Refresh Failure",
        "description": message,
        "assignment_group": assignment_group,
    }

    response = requests.post(
        servicenow_api_url,
        auth=(servicenow_username, servicenow_password),
        json=payload,
    )

    if response.status_code == 201:
        print("ServiceNow incident created successfully.")
        return {
        'statusCode': response.status_code,
        'body': json.dumps("ServiceNow incident created successfully.")
        }
        
    else:
        print(f"Failed to create ServiceNow incident with status code: {response.status_code}")
        return {
        'statusCode': response.status_code,
        'body': json.dumps(f"Failed to create ServiceNow incident with status code: {response.status_code}")
    }
        

def lambda_handler(event, context):
    # here calling the actual service now create incident
    responsePayload = create_servicenow_incident(event.get("message"), event.get("assignment_group"),
                               event.get("servicenow_api_url"), event.get("servicenow_username"), 
                               event.get("servicenow_password"))
                               
    return responsePayload
