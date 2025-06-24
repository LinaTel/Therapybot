# Therapybot (Headspace Helper)

A web-based mental health chatbot that provides supportive, document-grounded responses using a Retrieval-Augmented Generation (RAG) approach. The bot uses local embeddings and a language model to ensure answers are safe, respectful, and based on trusted resources.

## Features

- **Conversational AI**: Friendly chat interface for mental health support.
- **Document-grounded**: Answers are based only on a curated set of therapy and self-help documents.
- **Sensitive Topic Filtering**: Detects and gently redirects users away from topics that require professional intervention.
- **Profanity Filtering**: Ensures all conversations remain respectful.
- **Modern Web UI**: Responsive, clean interface with mascot and branding.
- **Session History**: Remembers the conversation during your session.

## How It Works

- User messages are checked for profanity and sensitive topics.
- If safe, the message is embedded and used to retrieve the most relevant therapy documents.
- The conversation history and retrieved documents are sent to a local language model (via Ollama) to generate a response.
- All AI responses are censored for profanity before being shown.

## Tech Stack

- **Backend**: Python, Flask, chromadb, ollama, better_profanity
- **Frontend**: HTML, CSS, JavaScript
- **Embeddings/LLM**: Local Ollama server (mental_helper model, mxbai-embed-large for embeddings)

## Setup Instructions

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) running locally with the `mental_helper` and `mxbai-embed-large` models
- (Optional) Virtual environment

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd Therapybot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama**
   - Make sure Ollama is running and the required models are available.

4. **Run the app**
   ```bash
   python Main.py
   ```
   The app will be available at `http://127.0.0.1:5000/`.

### File Structure

- `Main.py` — Flask app, chat logic, embedding, and filtering
- `therapy_docs.py` — Curated therapy/self-help documents
- `sensitive_topics.py` — List of topics to filter for user safety
- `templates/index.html` — Main web interface
- `static/style.css` — App styling
- `static/script.js` — Frontend chat logic
- `static/images/` — Mascot and logo images


## Security & Privacy

- No user data is stored long-term; session history is kept only for the duration of the browser session.
- The bot is not a substitute for professional help. Sensitive or crisis topics are redirected to appropriate resources.

## Acknowledgements

- Document content adapted from [TherapistAid.com](https://www.therapistaid.com/)
- Built with [Flask](https://flask.palletsprojects.com/), [chromadb](https://www.trychroma.com/), and [Ollama](https://ollama.com/) 