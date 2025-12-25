# GmailAIOrganizer

Label emails through Gmail with AI

## What it does

This connects to your Gmail inbox, reads your unread emails, and automatically applies labels (that you can choose) based on the subject and other factors. It uses Google's Gmail API and an LLM running with Ollama to classify each message. Labels are created if they don't already exist.

### Features

- Automatic Gmail authentication via OAuth2
- Reads messages for classification
- AI-powered email classification using a local LLM, which, by default, is Llama 3.1 8B with Ollama
- Creates labels if missing and applies them
- Category recommendations: Analyze your untagged emails and get AI-suggested new categories
- Customizable categories (see [model_wrapper.py](https://github.com/mintoleda/InboxOrganizer/blob/main/README.md#customizing-categories))
- Runs fully locally (no external LLM API required)
- Docker support for easy deployment

## Tools used

- Python
- Gmail API (google-auth, google-auth-oauthlib, google-api-python-client)
- Ollama
- Llama 3.1 8B (default)
- BeautifulSoup (HTML parsing)
- Docker (optional)

## How it works

1. Authenticate with Gmail using OAuth2.
2. Read unread emails from your inbox.
3. Extract subject, body, and sender from message(s)
4. Classify each email using local LLM.
5. Create a Gmail label if needed and apply it to the message.
6. Repeat for all unread messages.

## Setup

### 1) Create a Google Cloud project and enable Gmail API

1. Go to Google Cloud Console and create a project.
2. Enable the Gmail API for that project.
3. Configure OAuth consent screen:
   - User Type: "External"
   - Add scopes as needed (probably needs `.../auth/gmail.modify`)
4. Create OAuth 2.0 Client ID:
   - Application type: "Desktop app"
   - Download the client credentials JSON.
5. Save the file as `credentials.json` in the project's root directory.

### 2) Install and run the LLM 

1. Install Ollama from https://ollama.com
2. Start the Ollama service (should run on http://localhost:11434).
3. Pull the model used by this project:
   ```bash
   ollama pull llama3.1:8b
   ```
  - You can use any model you'd like as long as you make sure to edit `model_wrapper.py`
4. (Optional) Test that the model runs:
   ```bash
   ollama run llama3.1:8b "Classify this email about a bank statement."
   ```

### 3) Set up the Python environment

- Requires Python 3.10+

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
```bash
pip install -r requirements.txt
```

Note: The app expects Ollama to be running locally at `http://localhost:11434`. If you run Ollama elsewhere, set `OLLAMA_HOST` accordingly, e.g.:
```bash
export OLLAMA_HOST=http://127.0.0.1:11434
```

## First run and OAuth flow

- On the first run, the app will detect `credentials.json` and start a local OAuth flow:
  - After you approve, the app *locally* stores a `token.json` file for future runs.

If you ever need to re-authenticate, delete `token.json` and run the app again.

## Running the app

### Classify emails

Run the classifier with default settings (checks 10 emails, classifies up to 10):
```bash
python read_emails.py
```

With custom limits:
```bash
python read_emails.py --check 20 --classify 15
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--check N` | Total number of unread messages to check | 10 |
| `--classify N` | Number of messages to classify | 10 |
| `--recommend` | Recommend new categories based on untagged emails | - |

### Get category recommendations

Analyze your unread, untagged emails and get AI-suggested categories:
```bash
python read_emails.py --recommend
```

This will:
1. Fetch up to 50 unread emails that don't have any user labels
2. Analyze them with the LLM
3. Suggest up to 5 new categories (or confirm your current ones are sufficient)

Example output:
```
🔍 Analyzing unread, untagged emails for category recommendations...
Found 42 untagged emails to analyze.

💡 Suggested new categories:
   • Travel
   • Shopping
   • Newsletters

📝 To add these, edit the CATEGORIES list in model_wrapper.py
```

## Running with Docker

Build and run using Docker Compose:

```bash
# Build the image
docker compose build

# Run with default settings
docker compose run gmail-organizer

# Run with arguments
docker compose run gmail-organizer --recommend
docker compose run gmail-organizer --check 20 --classify 15
```

Note: Docker uses `host.docker.internal` to connect to Ollama running on your host machine. If Ollama is running elsewhere, modify the `OLLAMA_HOST` in `docker-compose.yml`.

## Customizing categories

- The classification categories and prompts can be adjusted in `model_wrapper.py`. You can add, remove, or rename categories as needed.

## Privacy and safety

- Your Gmail credentials (`credentials.json`) and tokens (`token.json`) stay on your machine.
- The LLM runs locally; no email content is sent to external LLM services.
- The app only creates/applies labels; it does not delete messages.

## Troubleshooting

- Missing or invalid credentials:
  - Ensure `credentials.json` is in the project root.
  - Delete `token.json` to re-authenticate if needed.
- Ollama/model not available:
  - Make sure the Ollama service is running (`ollama serve` if you run it manually).
  - Pull the model: `ollama pull llama3.1:8b`.
  - If running on a non-default host/port, set `OLLAMA_HOST`.
- Gmail API permission errors:
  - Ensure the OAuth consent screen is configured and the Gmail API is enabled.
  - Confirm the app has `gmail.modify` scope if it applies labels.
