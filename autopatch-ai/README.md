# AutoPatch AI

Autonomous PR Reviewer & Security Patching Agent powered by **NVIDIA Nemotron** on **Nebius Token Factory**.

## Project Architecture
- **Backend:** FastAPI, Uvicorn, PyGithub
- **AI Infrastructure:** Nebius Token Factory (NVIDIA Nemotron open-source model)
- **Track:** Coding and Agentic Engineering

## Setup Instructions
1. Extract the project ZIP.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API tokens:
   - `NEBIUS_API_KEY`
   - `GITHUB_TOKEN`
5. Start the webhook server:
   ```bash
   python app/main.py
   ```
6. Expose local port via ngrok:
   ```bash
   ngrok http 8000
   ```
7. Configure GitHub Webhook URL to `https://<ngrok_id>.ngrok-free.app/webhook` on `pull_request` events.
