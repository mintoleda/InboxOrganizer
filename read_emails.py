from gmail_auth import gmail_authenticate
import base64
import re
from bs4 import BeautifulSoup  # Optional, for cleaning HTML
from googleapiclient.errors import HttpError
from email_classifier import classify_email


# If you don't have it yet:
# pip install beautifulsoup4

def get_unread_messages(service, max_results=5):
    try:
        response = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
        return response.get('messages', [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def get_email_content(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = message['payload'].get('headers', [])

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')

    body = get_body_from_parts(message['payload'])

    return {
        'id': msg_id,
        'subject': subject,
        'body': body
    }


def get_body_from_parts(payload):
    """Recursively extracts plain text from payload parts"""
    if 'parts' in payload:
        for part in payload['parts']:
            result = get_body_from_parts(part)
            if result: return result
    else:
        mime_type = payload.get('mimeType', '')
        data = payload.get('body', {}).get('data', '')
        if mime_type == 'text/plain' and data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
        elif mime_type == 'text/html' and data:
            html = base64.urlsafe_b64decode(data).decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()

    return '(No readable content)'


if __name__ == '__main__':
    service = gmail_authenticate()
    unread = get_unread_messages(service)


    if not unread:
        print("No unread messages found.")
    else:
        print(f"Found {len(unread)} unread messages:\n")

        for msg in unread:
            email = get_email_content(service, msg['id'])
            label = classify_email(email['subject'], email['body'])
            print("🔹 Subject:", email['subject'])
            print("🏷️ Suggested Label:", label)
