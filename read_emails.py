from gmail_auth import gmail_authenticate
import base64
import re
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
from model_wrapper import classify_email_with_llm
import argparse

def get_unread_messages(service, max_results=1):
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

    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(No Sender)')

    return {
        'id': msg_id,
        'subject': subject,
        'body': body,
        'sender': sender
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

def apply_label_to_email(service, msg_id, label_id):
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={
            'addLabelIds': [label_id],
            'removeLabelIds': ['INBOX']
        }
    ).execute()


def get_or_create_label_id(service, label_name):
    """Returns the label ID for a given name, creating it if necessary"""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']

    # Create label if doesn't exist
    label_object = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }
    new_label = service.users().labels().create(userId='me', body=label_object).execute()
    return new_label['id']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gmail AI Organizer")
    parser.add_argument("--check", type=int, default=10, help="Total number of unread messages to check")
    parser.add_argument("--classify", type=int, default=10, help="Number of unread messages to classify")
    args = parser.parse_args()

    service = gmail_authenticate()
    unread = get_unread_messages(service, max_results=args.check)

    if not unread:
        print("No unread messages found.")
    else:
        print(f"Found {len(unread)} unread messages (checking up to {args.check}):\n")
        
        classified_count = 0

        for msg in unread:
            if classified_count >= args.classify:
                print(f"Reached classification limit of {args.classify}. Stopping.")
                break

            # Get full message details (including labels)
            message = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

            existing_labels = message.get('labelIds', [])

            # Define the AI labels you want to check for (case-insensitive)
            ai_labels = ["Work", "Finance", "Promotions", "Spam", "Scholarships", "Programming"] # Example labels; change at your own whim
            ai_label_ids = []

            # Get the label IDs for the AI labels

            # If any AI label ID is already in existing_labels, skip
            if any(label_id in existing_labels for label_id in ai_label_ids):
                print(f"Skipping message {msg['id']} - already labeled")
                continue

            print(f"[{classified_count + 1}/{args.classify}] Retrieving email content...")
            email = get_email_content(service, msg['id'])
            print("Classifying email...")
            label = classify_email_with_llm(email['subject'], email['body'], email['sender'])
            print("🔹 Subject:", email['subject'])
            print("👤 From:", email['sender'])
            print("🏷️ Suggested Label:", label)
            print("\n")

            # Get/create the label in Gmail
            label_id = get_or_create_label_id(service, label)

            apply_label_to_email(service, email['id'], label_id)
            
            classified_count += 1

            print("✅ Label applied!\n" + "-" * 40)
