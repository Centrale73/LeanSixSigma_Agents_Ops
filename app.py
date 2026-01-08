import asyncio
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel

from agents.worker import run_agent_with_governance
# from settings import settings # Unused in this file but good to have available

app = FastAPI(title="LSS Agentic Ops SaaS")

# --- Proactivity Engine (Watcher) ---
scheduler = AsyncIOScheduler()

async def watcher_service():
    """
    The 'Watcher Agent' (Proactivity Engine).
    Scans the system for scheduled tasks or predicted needs.
    """
    # [Logic Stub]: Connect to DB, check for 'recurring_reports' table
    # Example: If today == Monday, trigger "Market Report"
    print("--- [Proactivity Engine] Watcher scanning for pending goals... ---")
    
    # Simulated proactive trigger
    # In production, fetch this from PostgresAgentStorage metadata
    predicted_need = False 
    
    if predicted_need:
        print("--- [Proactivity Engine] Triggering Autonomous Task ---")
        run_agent_with_governance("Generate the Monday Market Update")

# --- API Models ---
class TaskRequest(BaseModel):
    query: str

# --- Routes ---

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(watcher_service, "interval", minutes=60)
    scheduler.start()

@app.post("/agent/run")
async def run_task(task: TaskRequest):
    """
    Trigger the Cognitive Core manually via REST API.
    """
    # Note: In a real async app, run_agent_with_governance might need to be awaited if the agent run is async
    # Agno's agent.run() is typically synchronous unless agent.arun() is used.
    # For this example, we keep it simple as per the prompt's snippet.
    result = run_agent_with_governance(task.query)
    return result

@app.get("/health")
def health_check():
    return {"status": "operational", "governance": "DMAIC Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)