# 💰 SmartSpend AI

> *Stop wondering where your money went. Start asking it.*

SmartSpend AI isn't just another dashboard—it's an **intelligent financial assistant** that lives on your laptop. I built this because I was tired of manually exporting CSVs and fighting with Excel formulas just to see if I spent too much on coffee.

Now, I just drag-and-drop my PDF statement, and within seconds, I’m chatting with my data.

![SmartSpend AI Demo](https://placehold.co/800x400?text=SmartSpend+AI+Dashboard)

## ✨ Why This Exists
Banking apps are great for checking balances, but terrible for *insights*. I wanted to answer questions like:
*   *"How much did I spend on Uber this month vs last month?"*
*   *"What are my recurring subscriptions?"*
*   *"Did I spend more than $500 on groceries?"*

Instead of clicking filters, I built a RAG-powered chatbot (using **Llama 3**) so I can just *ask*.

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

### 3. 💬 Privacy-First Financial Chat
I use **Ollama** to run Llama 3 locally. Your financial data never leaves your machine.
*   **RAG (Retrieval Augmented Generation):** The bot reads your recent transactions and gives context-aware answers.

## 🛠️ Tech Stack
I built this to be production-ready, not just a script.

*   **Frontend:** **Next.js 14** (App Router) + Tailwind CSS + Recharts
*   **Backend:** **Flask** (Python) + SQLAlchemy
*   **Machine Learning:** Scikit-Learn + Pandas
*   **GenAI:** Ollama (Llama 3)
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

---
*Built with ❤️ (and a lot of coffee) by Shabbir Hardwarewala.*
