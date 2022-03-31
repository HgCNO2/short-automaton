# Import Modules
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd


# Define function to get authorization
def gsc_auth(scopes):
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

    service = build('searchconsole', 'v1', credentials=creds)

    return service


# Authenticate API
scopes = ['https://www.googleapis.com/auth/webmasters']
service = gsc_auth(scopes)

# Build Question Query Regex
question_regex = r"\b(who|what|when|where|why|how|am|can|could|would|should|do|did|is|was|are|were|will|whom|whose|which)\b"

# Build Request Body
sa_request = {
    "startDate": "2022-01-01",
    "endDate": "2022-03-15",
    "dimensions": [
        "QUERY",
        "PAGE"
    ],
    "dimensionFilterGroups": [
        {
            "filters": [
                {
                    "dimension": "QUERY",
                    "operator": "INCLUDING_REGEX",
                    "expression": question_regex
                }
            ]
        }
    ],
    "rowLimit": 25000
}

# Make Request to GSC
gsc_search_analytics = service.searchanalytics().query(siteUrl='sc-domain:shortautomaton.com',
                                                       body=sa_request).execute()

gsc_df = pd.DataFrame(gsc_search_analytics['rows'])
