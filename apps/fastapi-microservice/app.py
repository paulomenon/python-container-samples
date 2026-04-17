from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastAPI Microservice", version="1.0.0")

tasks = []


class Task(BaseModel):
    title: str
    done: bool = False


@app.get("/")
def root():
    return {"message": "FastAPI Microservice", "docs": "/docs"}


@app.get("/tasks")
def list_tasks():
    return {"tasks": tasks}


@app.post("/tasks", status_code=201)
def create_task(task: Task):
    entry = {"id": len(tasks) + 1, **task.model_dump()}
    tasks.append(entry)
    return entry


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    existing = next((t for t in tasks if t["id"] == task_id), None)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")
    existing["title"] = task.title
    existing["done"] = task.done
    return existing
