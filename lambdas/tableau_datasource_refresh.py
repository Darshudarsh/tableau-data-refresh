import requests
import os
import boto3

# Tableau REST API
tableau_api_url = "https://your-tableau-server-url/api/3.12/auth/signin"

# Tableau Server authentication credentials
# Here im using token based authentication instead of basic authentication
# values are stored as env variables and accessing it
tableau_access_token_name = os.environ.get("tableau_access_token_name")
tableau_access_token_secret = os.environ.get("tableau_access_token_secret")

# Getting name of the project and data source to refresh from env
project_name = os.environ.get("myproject")
datasource_name = os.environ.get("mydatasource")

# Slack URL for the "#mychannel" channel
slack_webhook_url = os.environ.get("slack_web_url")

# ServiceNow API endpoint and credentials(stored in env)
servicenow_api_url = "https://your-servicenow-instance/api/now/table/incident"
servicenow_username = os.environ.get("servicenow_username")
servicenow_password = os.environ.get("servicenow_password")
assignment_group = "mygroup"  # defined as per the usecase group name

# Method to sign in to Tableau Server
def signin_tableau():
    payload = {
        "credentials": {
            "personalAccessTokenName": tableau_access_token_name,
            "personalAccessTokenSecret": tableau_access_token_secret
        }
    }

    # actual post request call to sign-in to tableau
    response = requests.post(tableau_api_url, json=payload)

    if response.status_code == 201:
        return response.json()["credentials"]["token"]
    else:
        error_message = {"message":"Failed to sign in to Tableau Server", "channel_name":"#mychannel"}
        
        # calling slack notification lambda function
        invoke_response = lambda_client.invoke(FunctionName='slack_notification', 
                        InvocationType='RequestResponse',
                        Payload=json.dumps(error_message))
        
        print(invoke_response['Payload'].read())

# Function to get the project and data source ID
# As per the use case only project name and data source name is provided but id's are required
def get_project_and_datasource_id(token):
    headers = {"Content-Type": "application/json", "X-Tableau-Auth": token}
    response = requests.get(f"https://tableau-server-url/api/3.12/sites/site-id/projects/{project_name}", headers=headers)

    if response.status_code == 200:
        project_id = response.json()["id"]
        response = requests.get(f"https://tableau-server-url/api/3.12/sites/site-id/projects/{project_id}/datasources", headers=headers)
        
        if response.status_code == 200:
            datasources = response.json()["datasources"]
            for datasource in datasources:
                if datasource["name"] == datasource_name:
                    return project_id, datasource["id"]
        
        error_message = {"message":"Data source not found in the project", "channel_name":"#mychannel"}
        
        # calling slack notification lambda function
        invoke_response = lambda_client.invoke(FunctionName='slack_notification', 
                        InvocationType='RequestResponse',
                        Payload=json.dumps(error_message))
                        
        print(invoke_response['Payload'].read())

    else:
        error_message = {"message":"Failed to retrieve project information", "channel_name":"#mychannel"}
        
        # calling slack notification lambda function
        invoke_response = lambda_client.invoke(FunctionName='slack_notification', 
                        InvocationType='RequestResponse',
                        Payload=json.dumps(error_message))
                        
        print(invoke_response['Payload'].read())

# Function to refresh the data source
def refresh_tableau_datasource():
    # calling sign function
    token = signin_tableau()
    
    # get tableau project_id and datasource_id
    project_id, datasource_id = get_project_and_datasource_id(token)
    
    # preparing the header and content to call tableau referesh API
    headers = {"Content-Type": "application/json", "X-Tableau-Auth": token}
    refresh_url = f"https://your-tableau-server-url/api/3.12/sites/your-site-id/projects/{project_id}/datasources/{datasource_id}/refresh"
    response = requests.post(refresh_url, headers=headers)

    if response.status_code == 202:
        success_message = {"message":"Tableau data source refresh succeeded.", "channel_name":"#mychannel"}
        
        # calling slack notification lambda function
        invoke_response = lambda_client.invoke(FunctionName='slack_notification', 
                        InvocationType='RequestResponse',
                        Payload=json.dumps(success_message))
                        
        print(invoke_response['Payload'].['body'].read())
    else:
        # In the case of failure to refresh data, sending slack message and creating the service now incident
        slack_error_message = {"message": "Tableau data source refresh failed.", "channel_name": "#mychannel"}

        # calling slack notification lambda function
        slack_invoke_response = lambda_client.invoke(FunctionName='slack_notification',
                                               InvocationType='RequestResponse',
                                               Payload=json.dumps(slack_error_message))

        print(slack_invoke_response['Payload'].read())

        # In the case of error, raise the service incident ticket
        payload = {"message":f"Data source refresh request failed with status code: {response.status_code}",
                    "assignment_group": assignment_group,
                    "servicenow_api_url": servicenow_api_url,
                    "servicenow_username": servicenow_username,
                    "servicenow_password": servicenow_password
        }
        
        # calling servicenow incident lambda function
        service_now_invoke_response = lambda_client.invoke(FunctionName='service_now_incident',
                        InvocationType='RequestResponse',
                        Payload=json.dumps(payload))
                        
         print(service_now_invoke_response['Payload'].read())

def lambda_handler(event, context):
    refresh_tableau_datasource()
