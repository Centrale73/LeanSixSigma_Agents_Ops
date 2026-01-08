# Lean Six Sigma Agentic Ops (LSS-Agents)

**An Agentic Productivity SaaS that operationalizes "Lean Six Sigma (LSS)" as a governance layer for Autonomous Cognitive Agents.**

This project implements a **Symbiotic Architecture** where a highly capable AI Agent (Cognitive Core) is strictly governed by a logical constraint (DMAIC Workflow) and driven by an autonomous background service (Proactivity Engine).

## 🏗️ Architecture

1.  **The Cognitive Core (The Agent)**:
    *   Powered by **Agno (Phidata)** and **Perplexity AI**.
    *   Uses **FastEmbed** for local, privacy-preserving vector embeddings.
    *   Persists long-term memory and knowledge in **PostgreSQL (pgvector)**.

2.  **The LSS Governance Layer (The Constraint)**:
    *   Every agent action is wrapped in a **DMAIC Workflow** (Define, Measure, Analyze, Improve, Control).
    *   A **Self-Correction Loop** automatically retries tasks if the agent's self-assessed confidence ("Control" score) is below 80%.

3.  **The Proactivity Engine (The Autonomy)**:
    *   A background **Watcher Service** (using `apscheduler`) scans for predicted needs and triggers the agent without user input.

## 🛠️ Tech Stack

*   **Framework**: [Agno](https://github.com/agno-agi/agno) (Python)
*   **LLM**: [Perplexity API](https://docs.perplexity.ai/) (`sonar-pro`)
*   **API**: FastAPI
*   **Database**: PostgreSQL + pgvector
*   **Embeddings**: FastEmbed (Local)

## 🚀 Setup Instructions

### Prerequisites

*   Python 3.10+
*   PostgreSQL running locally or in the cloud.
*   A Perplexity API Key.

### 1. Clone the Repository

```bash
git clone https://github.com/Lmao53and2/LeanSixSigma_Agents_Ops.git
cd LeanSixSigma_Agents_Ops
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
# API Keys
AGNO_API_KEY=your_agno_key_here
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxx

# Optional: For future expansion
GROQ_API_KEY=
OPENROUTER_API_KEY=

# Database Configuration
# Format: postgresql+psycopg://user:password@host:port/dbname
DATABASE_URL=postgresql+psycopg://ai:ai@localhost:5532/ai
```

### 4. Run the Application

Start the FastAPI server and the Autonomous Watcher service:

```bash
python app.py
```

The API will be available at `http://0.0.0.0:8000`.

## 🧠 Usage

### Manual Trigger (API)

Send a POST request to `/agent/run` with your task:

```json
POST /agent/run
{
  "query": "Research the impact of AI agents on supply chain logistics and propose an optimization strategy."
}
```

The agent will respond with a structured **DMAIC JSON** object:

```json
{
  "define": "User wants to optimize supply chain logistics using AI agents.",
  "measure": "Success defined by actionable strategies with >15% efficiency gain potential.",
  "analyze": "Perplexity search results on autonomous logistics...",
  "improve": "Proposed Strategy: Deploy multi-agent systems for predictive inventory management...",
  "control": 85
}
```

### Autonomous Trigger

The background scheduler (configured in `app.py`) runs every hour to check for pending goals. (Logic stubbed in `watcher_service`).

## 📂 Project Structure

*   `agents/worker.py`: The core `ProductivityAgent` with LSS logic and Self-Correction loop.
*   `models/lss.py`: Pydantic models enforcing the DMAIC structure.
*   `tools/perplexity.py`: Tool definitions for deep research.
*   `app.py`: FastAPI entry point and Proactivity Engine.
*   `settings.py`: Configuration management.

---

**License**: MIT
