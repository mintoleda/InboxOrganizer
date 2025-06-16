from __future__ import print_function
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]


def gmail_authenticate():
    creds = None

    # Check if token.json already exists
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials available, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load credentials.json you downloaded
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service


# Sample usage:
if __name__ == '__main__':
    service = gmail_authenticate()
    profile = service.users().getProfile(userId='me').execute()
    print(f"Authenticated as: {profile['emailAddress']}")
