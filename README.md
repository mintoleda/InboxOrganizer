# GmailAIOrganizer

Label emails through Gmail with AI

## Overview

GmailAIOrganizer is a Python project that automatically classifies and labels your Gmail emails using AI. It leverages the Gmail API to read unread messages and applies smart labels by using a local AI model (via Ollama and Mistral) to categorize each email.

## Features

- **Automatic Gmail authentication** via OAuth2, with token storage for seamless future use.
- **Reads unread Gmail messages** using the Gmail API.
- **AI-powered email classification**: Emails are categorized using a local AI model into categories such as:
  - Work
  - Finance
  - Promotions
  - Spam
  - Scholarships
  - Github
  - Programming
- **Automatic label management**: Creates new Gmail labels if they do not exist and applies them to emails.
- **HTML email parsing**: Cleans up HTML content for proper classification.
- **Extensible categories**: Add or modify categories in `gemma_wrapper.py`.

## Technologies Used

- **Python**
- **Google Gmail API** (`google-auth`, `google-auth-oauthlib`, `google-api-python-client`)
- **Ollama** (for running local LLMs)
- **Mistral 7B** (default model for classification)
- **BeautifulSoup** (for HTML parsing)
- **Re** (regular expressions)

## How It Works

1. **Authenticate with Gmail** using OAuth2.
2. **Read unread emails** from the inbox.
3. **Extract email content** (subject, body, sender).
4. **Classify each email** using the AI model (see `gemma_wrapper.py`).
5. **Determine the appropriate label** and apply it to the message (creating the label if needed).
6. **Repeat for all unread messages**.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mintoleda/GmailAIOrganizer.git
   cd GmailAIOrganizer