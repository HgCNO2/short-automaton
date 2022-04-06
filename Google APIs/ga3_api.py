# Import Modules
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
from collections import defaultdict


# Define function to get authorization
def ga_auth(scopes):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('analyticsreporting', 'v4', credentials=creds)

    return service


# Set Scopes
scopes = ['https://www.googleapis.com/auth/analytics.readonly']

# Authenticate & Build Service
analytics = ga_auth(scopes)

# Set Request Parameters
views = {'Short Automaton': '262445554'}
dimensions = ['ga:sourceMedium']
metrics = ['ga:sessions']

# Build request body
body = {
    "reportRequests": [
        {
            "viewId": views['Short Automaton'],
            "dateRanges": [
                {
                    "startDate": "2022-03-01",
                    "endDate": "2022-03-31"
                }
            ],
            "dimensions": [{'name': dimension} for dimension in dimensions],
            "metrics": [{'expression': metric} for metric in metrics],
            "pageSize": 100000,
            "samplingLevel": "LARGE"
        }
    ]
}

# Make Request
response = analytics.reports().batchGet(body=body).execute()

# Parse Request
report_data = defaultdict(list)

for report in response.get('reports', []):
    rows = report.get('data', {}).get('rows', [])
    for row in rows:
        for i, key in enumerate(dimensions):
            report_data[key].append(row.get('dimensions', [])[i])  # Get dimensions

        for values in row.get('metrics', []):
            all_values = values.get('values', [])  # Get metric values
            for i, key in enumerate(metrics):
                report_data[key].append(all_values[i])

report_df = pd.DataFrame(report_data)
