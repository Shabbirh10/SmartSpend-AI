# 💰 SmartSpend AI

> *Stop wondering where your money went. Start asking it.*

SmartSpend AI isn't just another dashboard—it's an **intelligent financial assistant** that lives on your laptop. I built this because I was tired of manually exporting CSVs and fighting with Excel formulas just to see if I spent too much on coffee.

Now, I just drag-and-drop my PDF statement, and within seconds, I’m chatting with my data.

![SmartSpend AI Dashboard](assets/dashboard.png)

## ✨ Why This Exists
Banking apps are great for checking balances, but terrible for *insights*. I wanted to answer questions like:
*   *"How much did I spend on Uber this month vs last month?"*
*   *"What are my recurring subscriptions?"*
*   *"Did I spend more than $500 on groceries?"*

Instead of clicking filters, I built a RAG-powered chatbot (using **Gemini**) so I can just *ask*.

## 🚀 Features Under the Hood

### 1. 🧠 Hybrid Parsing Engine
PDFs are messy. I use a hybrid approach:
*   **Regex** for the easy stuff (dates, amounts).
*   **LLM Fallback** for the weirdly formatted lines that usually break parsers.
*   *Result:* It parses statements that other tools choke on.

### 2. 🤖 Custom ML Classification
I didn't want to rely on generic APIs. I trained a **Random Forest Classifier** (using Scikit-Learn) on transaction descriptions.
*   **Input:** "AMZN MKTP US*1A2B" -> **Output:** "Shopping"
*   It learns from my data and gets smarter over time.

### 3. 💬 AI-Powered Financial Chat
I use **Google Gemini API** to power the chatbot.
*   **RAG (Retrieval Augmented Generation):** The bot reads your recent transactions and gives context-aware answers.

## 🛠️ Tech Stack
I built this to be production-ready, not just a script.

*   **Frontend:** **Next.js** (App Router) + Tailwind CSS + Recharts
*   **Backend:** **Flask** (Python) + SQLAlchemy
*   **Machine Learning:** Scikit-Learn + Pandas
*   **GenAI:** Google Gemini API
*   **Database:** PostgreSQL / SQLite

## ⚡ Quick Start

I've included a **Demo Mode** so you can try it instantly.

1.  **Clone & Setup**
    ```bash
    git clone https://github.com/Shabbirh10/SmartSpend-AI.git
    cd SmartSpend-AI
    ./start_app.sh
    ```

2.  **That's it.**
    *   The script sets up the database, trains the ML model, and launches the servers.
    *   Go to `http://localhost:3000`.

3.  **Try the Demo**
    *   Click **"Sample PDF"** in the top right to download a realistic (but fake) statement.
    *   Upload it and watch the AI analyze 80+ transactions in real-time.

## 🔮 What's Next?
*   Adding support for multi-statement trend analysis.
*   Dockerizing the entire stack for one-click deployment.
*   Fine-tuning a smaller model (like Phi-3) for even faster CPU inference.

## 🐳 Docker (one command)
If you have Docker Desktop running:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000/health`

## 🌐 Deploy (recruiter-ready)
This repo deploys cleanly as **2 services**: a Flask API + a Next.js web app.

### Backend (Render)
- **Service type**: Web Service
- **Root directory**: `backend`
- **Build command**:

```bash
pip install -r requirements.txt
```

- **Start command**:

```bash
PYTHONPATH=.. python init_db.py && PYTHONPATH=.. gunicorn -w 2 -b 0.0.0.0:$PORT wsgi:app
```

After deploy, your API base URL will look like:
- `https://<your-render-service>.onrender.com/api`

### Frontend (Vercel)
- Import the `frontend` directory as a Vercel project.
- Set the environment variable:
  - `NEXT_PUBLIC_API_URL` = `https://<your-render-service>.onrender.com/api`

Deploy, then open your Vercel URL and you’re ready to demo.

### Notes
- **Gemini API**: The chat endpoint uses Google's Gemini API for fast and intelligent responses. Ensure your API key is correctly configured.
- **ML model**: The backend auto-trains a compatible classifier if the bundled pickle is missing/incompatible.

---
*Built with ❤️ (and a lot of coffee) by Shabbir Hardwarewala.*
