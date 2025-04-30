# 🧠 Multi-Tool Agent with LangGraph

**Build a Tool-Calling AI Agent** with memory, history tracking, and dynamic tool selection using [LangGraph](https://github.com/langchain-ai/langgraph), [ChatGroq](https://groq.com/), and external tools like Arxiv, Wikipedia, and Tavily.

This project creates a local agent capable of answering questions by deciding whether to use an LLM or invoke tools like search or academic databases — all orchestrated through a LangGraph state machine and accessible via a Streamlit frontend.

---

## ⚙️ Features

- 🔁 Agent with memory (via LangGraph's `MemorySaver`)
- 🧰 Tool selection via `ToolNode` and conditional routing
- 📚 Tools: Arxiv, Wikipedia, Tavily Web Search
- 🧠 LLM with tool-binding (Groq's `qwen-qwq-32b`)
- 💬 Supports threaded chat history
- 📊 Streamlit UI (optional interface layer)

---

## 📁 Project Structure

```
.
├── app.py                 # Streamlit interface
├── agent.py               # LangGraph agent logic (core)
├── tools.py               # External tools configuration
├── utils.py               # utilities for rendering interface
├── .env                   # API keys (TAVILY_API_KEY, GROQ_API_KEY)
```

---

## 🧩 Requirements

- Python 3.9+
- [Groq CLI](https://groq.com/) account + API Key
- [Tavily](https://www.tavily.com/) API key
- Arxiv and Wikipedia access (via LangChain wrappers)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/langgraph-agent.git
cd langgraph-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Setup Environment

Create a `.env` file in the root directory:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## 🧪 Run Agent (CLI Mode)

```bash
python agent.py
```

You'll be prompted to enter a query. The agent will respond using the most relevant tools.

---

## 🖥️ Run with Streamlit UI

If you've created a `Streamlit` interface (e.g. `app.py`), run:

```bash
streamlit run app.py
```

---

## 🧠 How It Works

1. The agent builds a **LangGraph state machine**.
2. The LLM receives messages and decides whether tools are needed.
3. If a tool is required, the graph conditionally routes the message to the right tool.
4. Messages are returned to the LLM for final output.
5. The `MemorySaver` retains conversation context across turns.

---

## 🛠 Tools Used

- **Arxiv** – academic paper search
- **Wikipedia** – encyclopedia lookup
- **Tavily** – web search engine
- **LangGraph** – stateful agent workflow engine
- **ChatGroq** – high-performance LLM backend

---
