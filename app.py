import asyncio
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel

from agents.worker import harness

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
        harness.run("Generate the Monday Market Update")

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
    Uses DMAICHarness to wrap the ProductivityAgent with DMAIC governance.
    """
    result = harness.run(task.query)
    return result

@app.get("/health")
def health_check():
    return {"status": "operational", "governance": "DMAIC Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
