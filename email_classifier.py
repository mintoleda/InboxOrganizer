import google.generativeai as genai
import re

# Load your Gemini API key
genai.configure(api_key="AIzaSyA3mgeMYJDsfiajXE1A44gEEj-wrBdWu1g")

# Initialize model (you can choose 'gemini-pro' or others)
genai.list_models()
model = genai.GenerativeModel("gemini-pro")

# MAIN FUNCTION: Classify email using Gemini, fallback to rules
def classify_email(subject, body):
    genai.list_models()
    try:
        # Build prompt for Gemini
        prompt = f"""
You are an email categorization assistant.

Given this email, assign one of the following categories:
- Work
- Personal
- Finance
- Promotions
- Spam
- Social
- Updates
- Uncategorized

Subject: {subject}
Body: {body[:200]}  # truncate for token efficiency

Respond with only the category name.
"""

        response = model.generate_content(prompt)
        label = response.text.strip()

        # Basic cleanup
        label = re.sub(r"[^a-zA-Z]", "", label).capitalize()

        if label not in ["Work", "Personal", "Finance", "Promotions", "Spam", "Social", "Updates", "Uncategorized"]:
            print("⚠️ Gemini gave unclear label. Using fallback.")
            return fallback_label(subject, body)

        return label

    except Exception as e:
        print("❌ Gemini API failed:", e)
        return fallback_label(subject, body)

# FALLBACK: Simple keyword rule-based logic
def fallback_label(subject, body):
    text = f"{subject} {body}".lower()

    if any(word in text for word in ["invoice", "payment", "bank", "receipt", "transaction"]):
        return "Finance"
    elif any(word in text for word in ["unsubscribe", "offer", "discount", "promo", "sale"]):
        return "Promotions"
    elif any(word in text for word in ["meeting", "deadline", "project", "schedule", "work"]):
        return "Work"
    elif any(word in text for word in ["mom", "dad", "family", "home"]):
        return "Personal"
    elif any(word in text for word in ["friend", "party", "social", "hangout"]):
        return "Social"
    elif "update" in text:
        return "Updates"
    elif "spam" in text or "lottery" in text or "click here" in text:
        return "Spam"
    else:
        return "Uncategorized"
