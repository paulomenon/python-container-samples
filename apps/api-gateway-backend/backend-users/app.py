"""User CRUD API."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Users Backend")

_users: dict[int, dict] = {}
_next_id = 1


class UserCreate(BaseModel):
    name: str
    email: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


@app.get("/users")
def list_users():
    return list(_users.values())


@app.post("/users", status_code=201)
def create_user(body: UserCreate):
    global _next_id
    uid = _next_id
    _next_id += 1
    user = {"id": uid, "name": body.name, "email": body.email}
    _users[uid] = user
    return user


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    return _users[user_id]


@app.put("/users/{user_id}")
def replace_user(user_id: int, body: UserCreate):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    _users[user_id] = {"id": user_id, "name": body.name, "email": body.email}
    return _users[user_id]


@app.patch("/users/{user_id}")
def patch_user(user_id: int, body: UserUpdate):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    data = _users[user_id]
    if body.name is not None:
        data["name"] = body.name
    if body.email is not None:
        data["email"] = body.email
    return data


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    del _users[user_id]
