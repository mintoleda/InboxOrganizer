from ollama import Client
import re

client = Client(host='http://localhost:11434')
CATEGORIES = ["Work", "Finance", "Promotions", "Spam", "Scholarships", "Github", "Programming"]

def classify_email_with_gemma(subject: str, body: str, sender: str) -> str:
    prompt = f"""
You are a smart AI assistant that classifies emails into these categories:
{', '.join(CATEGORIES)}.

Take into account the sender's address or name (if available) when deciding the category.
If the email does not fit any of these categories, return "Uncategorized".

Sender: {sender}
Subject: {subject}
Body: {body[:3000]}

Return only the category name.
"""

    try:
        response = client.generate(model="gemma3:1b", prompt=prompt)
        label = response["response"].strip()
        label = re.sub(r"[^a-zA-Z]", "", label).capitalize()

        if label not in CATEGORIES:
            return "Uncategorized"

        return label
    except Exception as e:
        print("❌ Error calling Gemma:", e)
        return "Uncategorized"
