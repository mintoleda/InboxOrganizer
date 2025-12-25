from ollama import Client
import re
import os

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
client = Client(host=OLLAMA_HOST)
CATEGORIES = ["Work", "Finance", "Promotions", "Spam"]


def suggest_new_categories(email_samples: list[dict]) -> list[str]:
    if not email_samples:
        return []


    email_summaries = []
    for i, email in enumerate(email_samples[:50], 1):
        summary = f"{i}. From: {email.get('sender', 'Unknown')} | Subject: {email.get('subject', '(No Subject)')}"
        email_summaries.append(summary)

    emails_text = "\n".join(email_summaries)

    prompt = f"""You are analyzing a user's email inbox to suggest new category labels.

Current categories: {', '.join(CATEGORIES)}

Here are summaries of recent untagged emails:
{emails_text}

Based on these emails, suggest up to 5 NEW category names that would help organize this inbox.
- Only suggest categories that are clearly needed based on the emails shown.
- Do NOT suggest categories that already exist or are similar to existing ones.
- If no new categories are needed, respond with exactly: NONE

Return ONLY a comma-separated list of category names (e.g., "Travel, Shopping, News") or "NONE".
"""

    try:
        response = client.generate(model="llama3.1:8b", prompt=prompt)
        result = response["response"].strip()

        if result.upper() == "NONE" or not result:
            return []

        raw_categories = [cat.strip() for cat in result.split(",")]
        categories = []
        for cat in raw_categories:
            cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", cat).strip().title()
            # Only accept 1-2 word category names to filter out LLM rambling
            if cleaned and len(cleaned.split()) <= 2:
                categories.append(cleaned)
        return categories[:5]

    except Exception as e:
        print(f"❌ Error getting category suggestions: {e}")
        return []


def classify_email_with_llm(subject: str, body: str, sender: str) -> str:
    prompt = f"""
You are a smart AI assistant that classifies emails into these categories:
{', '.join(CATEGORIES)}.

Take into account the sender's address or name (if available) when deciding the category.
If the email does not fit any of these categories, return "Uncategorized".

Sender: {sender}
Subject: {subject}
Body: {body[:250]}

Return only the category name.
"""

    try:
        response = client.generate(model="llama3.1:8b", prompt=prompt)
        label = response["response"].strip()
        label = re.sub(r"[^a-zA-Z]", "", label).capitalize()

        if label not in CATEGORIES:
            return "Uncategorized"

        return label
    except Exception as e:
        print("❌ Error calling LLM:", e)
        return "Uncategorized"
