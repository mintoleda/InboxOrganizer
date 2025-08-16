# GmailAIOrganizer

Label emails through Gmail with AI

## What it does

GmailAIOrganizer connects to your Gmail account, reads your unread emails, and automatically applies smart labels based on the content. It uses the Gmail API for access and a local Large Language Model (LLM) running via Ollama (Mistral 7B by default) to classify each message. Labels are created if they don’t exist and applied to the right emails so your inbox stays organized.

### Features

- Automatic Gmail authentication via OAuth2 with token caching for seamless reuse
- Reads unread messages and parses HTML safely for classification
- AI-powered email classification using a local LLM (Mistral 7B via Ollama)
- Automatic label management: creates labels if missing and applies them
- Extensible categories you can customize (see gemma_wrapper.py)
- Runs fully locally for inference (no external LLM API required)

## Tech stack

- Python
- Gmail API (google-auth, google-auth-oauthlib, google-api-python-client)
- Ollama (local LLM runtime)
- Mistral 7B (default model via Ollama)
- BeautifulSoup (HTML parsing)
- re (regular expressions)

## How it works (high level)

1. Authenticate with Gmail using OAuth2.
2. Read unread emails from your inbox.
3. Extract message content (subject, body, sender).
4. Classify each email using the local LLM (Mistral 7B via Ollama).
5. Create a Gmail label if needed and apply it to the message.
6. Repeat for all unread messages.

## Setup

### 1) Create a Google Cloud project and enable Gmail API

1. Go to Google Cloud Console and create a project.
2. Enable the “Gmail API” for that project.
3. Configure OAuth consent screen:
   - User Type: “External” (fine for personal use)
   - Add scopes as needed (the app typically uses `.../auth/gmail.modify`)
4. Create OAuth 2.0 Client ID:
   - Application type: “Desktop app”
   - Download the client credentials JSON.
5. Save the file as `credentials.json` in the project root (next to your code).
   - Important: Do not commit `credentials.json` to version control.

Tip: Add both `credentials.json` and `token.json` to your `.gitignore`.

### 2) Install and run the local LLM (Ollama + Mistral 7B)

1. Install Ollama from https://ollama.com
2. Start the Ollama service (it usually runs on http://localhost:11434).
3. Pull the model used by this project:
   ```bash
   ollama pull mistral
   ```
4. (Optional) Test that the model runs:
   ```bash
   ollama run mistral "Classify this email about a bank statement."
   ```

### 3) Set up the Python environment

- Requires Python 3.10+ (recommended)

Clone the repository:
```bash
git clone https://github.com/mintoleda/GmailAIOrganizer.git
cd GmailAIOrganizer
```

Create and activate a virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

Install dependencies:
- If the project includes a requirements file:
  ```bash
  pip install -r requirements.txt
  ```
- Otherwise, install the common dependencies:
  ```bash
  pip install google-api-python-client google-auth google-auth-oauthlib beautifulsoup4 ollama
  ```

Note: The app expects Ollama to be running locally at `http://localhost:11434`. If you run Ollama elsewhere, set `OLLAMA_HOST` accordingly, e.g.:
```bash
export OLLAMA_HOST=http://127.0.0.1:11434
```

## First run and OAuth flow

- On the first run, the app will detect `credentials.json` and start a local OAuth flow:
  - A browser window opens prompting you to log in and grant Gmail permissions.
  - After you approve, the app exchanges the code and stores a `token.json` file locally for future runs.
- By default, `token.json` is saved in the project directory. Do not commit it.

If you ever need to re-authenticate, delete `token.json` and run the app again.

## Running the app

Run the classifier:
```bash
python main.py
```

Notes:
- Ensure Ollama is running and the `mistral` model is available (`ollama pull mistral`).
- Ensure `credentials.json` is present in the project root.

What you should see:
- On first run: an OAuth browser flow, then the app prints that it’s authorized.
- Terminal logs indicating:
  - Number of unread messages fetched
  - For each email: subject, chosen category, and label creation/application status
  - A summary of processed messages and labels applied

Example (illustrative):
```
Authenticating with Gmail...
Token loaded from token.json
Fetching unread messages...
Processing: "Your invoice for July" -> Classified as "Finance"
Label "Finance" found. Applying label...
Processing: "GitHub: new issue in repo" -> Classified as "Github"
Label "Github" not found. Creating label...
Done. 8 messages processed, 8 labeled.
```

## Customizing categories

- The classification categories and prompts can be adjusted in `gemma_wrapper.py`. You can add, remove, or rename categories as needed to fit your workflow.

## Privacy and safety

- Your Gmail credentials (`credentials.json`) and tokens (`token.json`) stay on your machine.
- The LLM runs locally via Ollama; no email content is sent to external LLM services.
- The app only creates/applies labels; it does not delete messages.

## Troubleshooting

- Missing or invalid credentials:
  - Ensure `credentials.json` is in the project root.
  - Delete `token.json` to re-authenticate if needed.
- Ollama/model not available:
  - Make sure the Ollama service is running (`ollama serve` if you run it manually).
  - Pull the model: `ollama pull mistral`.
  - If running on a non-default host/port, set `OLLAMA_HOST`.
- Gmail API permission errors:
  - Ensure the OAuth consent screen is configured and the Gmail API is enabled.
  - Confirm the app has `gmail.modify` scope if it applies labels.
