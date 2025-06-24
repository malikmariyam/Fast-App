from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
import uuid

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session file path
SESSION_FILE = 'database/session/session.json'
os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
if not os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, 'w') as f:
        json.dump({}, f)

# Global session dictionary
session_data = {}

# ---------- A. Home Route ----------


@app.get("/")
def home():
    return "Home Route"

# ---------- B. Get User Info (static list) ----------


@app.get("/users")
def get_users():
    users = [
        {"name": "Ali", "age": 25, "gender": "Male"},
        {"name": "Sara", "age": 22, "gender": "Female"},
        {"name": "Zain", "age": 30, "gender": "Male"},
        {"name": "Hina", "age": 28, "gender": "Female"},
        {"name": "Tariq", "age": 26, "gender": "Male"}
    ]
    return users

# ---------- C. Add User Info with Session ----------


@app.post("/add-user")
async def add_user(request: Request, api_key: str = Header(None)):
    try:
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")
        if api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # ✅ Await the JSON properly
        data = await request.json()

        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")

        session_id = str(uuid.uuid4())
        session_data[session_id] = {"name": name, "age": age, "gender": gender}
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f, indent=4)

        return {"session_id": session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ---------- D. Get User by Session ID ----------


@app.post("/get-user")
async def get_user(request: Request, api_key: str = Header(None)):
    try:
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")
        if api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        body = await request.json()
        session_id = body.get("session_id")

        if session_id not in session_data:
            raise HTTPException(status_code=404, detail="Session ID not found")

        return session_data[session_id]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
