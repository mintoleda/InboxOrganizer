from gmail_auth import gmail_authenticate
import base64
import re
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
from model_wrapper import classify_email_with_llm, suggest_new_categories, CATEGORIES
import argparse


def get_user_label_ids(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    user_label_ids = {label['id'] for label in labels if label.get('type') == 'user'}
    return user_label_ids


def get_unread_untagged_messages(service, max_results=50):
    try:
        response = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
        messages = response.get('messages', [])
        
        if not messages:
            return []
        
        user_label_ids = get_user_label_ids(service)
        untagged = []
        
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
            existing_labels = set(message.get('labelIds', []))
            

            if not existing_labels.intersection(user_label_ids):
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(No Sender)')
                untagged.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender
                })
        
        return untagged
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


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
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']


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
    parser.add_argument("--recommend", action="store_true", help="Recommend new categories based on untagged emails")
    args = parser.parse_args()

    service = gmail_authenticate()


    if args.recommend:
        print("🔍 Analyzing unread, untagged emails for category recommendations...")
        untagged = get_unread_untagged_messages(service, max_results=50)
        
        if not untagged:
            print("No unread, untagged messages found.")
        else:
            print(f"Found {len(untagged)} untagged emails to analyze.\n")
            suggestions = suggest_new_categories(untagged)
            
            if not suggestions:
                print("✅ No new categories recommended. Your current categories seem sufficient:")
                print(f"   Current: {', '.join(CATEGORIES)}")
            else:
                print("💡 Suggested new categories:")
                for cat in suggestions:
                    print(f"   • {cat}")
                print(f"\n📝 To add these, edit the CATEGORIES list in model_wrapper.py")
        exit(0)


    unread = get_unread_messages(service, max_results=args.check)

    if not unread:
        print("No unread messages found.")
    else:
        print(f"Found {len(unread)} unread messages (checking up to {args.check}):\n")
        
        classified_count = 0
        user_label_ids = get_user_label_ids(service)

        for msg in unread:
            if classified_count >= args.classify:
                print(f"Reached classification limit of {args.classify}. Stopping.")
                break


            message = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

            existing_labels = set(message.get('labelIds', []))


            if existing_labels.intersection(user_label_ids):
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


            label_id = get_or_create_label_id(service, label)

            apply_label_to_email(service, email['id'], label_id)
            
            classified_count += 1

            print("✅ Label applied!\n" + "-" * 40)

