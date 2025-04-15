from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
from datetime import datetime
from collections import deque
import time

app = FastAPI()
class StatusRecord(BaseModel):
    status: int
    timestamp: datetime

class TaskIn(BaseModel):
    name: str
    difficulty: int

class TaskOut(TaskIn):
    id: int
    status_history: List[StatusRecord]

mock_db = {}
task_counter = 1

request_times = deque()
WINDOW_SECONDS = 1

@app.middleware("http")
async def count_requests(request: Request, call_next):
    now = time.time()
    request_times.append(now)

    while request_times and request_times[0] < now - WINDOW_SECONDS:
        request_times.popleft()

    response = await call_next(request)
    return response

@app.get("/stats")
async def get_stats():
    return {
        "rps": len(request_times),
        "window_sec": WINDOW_SECONDS,
        "total_requests_in_window": len(request_times)
    }

@app.post("/api/v1/task", response_model=TaskOut)
async def create_task(task: TaskIn):
    global task_counter
    task_id = task_counter
    task_counter += 1

    status_history = [
        StatusRecord(status=1, timestamp=datetime.utcnow())
    ]

    task_data = TaskOut(
        id=task_id,
        name=task.name,
        difficulty=task.difficulty,
        status_history=status_history
    )

    mock_db[task_id] = task_data
    return task_data

@app.get("/api/v1/task/{id}", response_model=TaskOut)
async def get_task(id: int):
    task = mock_db.get(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_server:app", host="0.0.0.0", port=8000, reload=True)
