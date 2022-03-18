# Import Modules
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


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


# Define List of Sites Function
def get_sites(service):
    return service.sites().list().execute()


# Define List of Sitemaps Function
def get_sitemaps(service, property_uri):
    return service.sitemaps().list(siteUrl=property_uri).execute()


# Define Query Execution Function
def query_gsc(service, property_uri, request):
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()


# Define Inspect URL Function
def inspect_url(service, request):
    return service.urlInspection().index().inspect(body=request).execute()


if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/webmasters']
    service = gsc_auth(scopes)
    gsc_sites = get_sites(service)
    gsc_sitemaps = get_sitemaps(service, 'sc-domain:shortautomaton.com')

    sa_request = {
        "startDate": "2022-03-01",
        "endDate": "2022-03-15",
        "dimensions": [
            "QUERY",
            "PAGE"
        ],
        "rowLimit": 10
    }

    gsc_search_analytics = query_gsc(service, 'sc-domain:shortautomaton.com', sa_request)

    inspect_request = {
        "siteUrl": "sc-domain:shortautomaton.com",
        "inspectionUrl": "https://www.shortautomaton.com/",
    }

    gsc_inspect = inspect_url(service, inspect_request)
