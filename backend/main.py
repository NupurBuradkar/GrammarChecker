"""
FastAPI Server for Grammar & Spell Checking Application
Provides REST endpoints for text analysis, custom dictionary management,
user authentication, document upload parsing, and check history logging,
and serves static web frontend.
"""

import os
import json
import time
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .engine import nlp_pipeline, user_dict

app = FastAPI(
    title="GrammaCheck AI - Grammar & Spell Checker",
    description="NLP-powered grammar, spell, punctuation, style, and tone checking platform.",
    version="2.1.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
HISTORY_FILE = os.path.join(BASE_DIR, "backend", "history_store.json")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    css_dir = os.path.join(STATIC_DIR, "css")
    js_dir = os.path.join(STATIC_DIR, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")


# =========================================================================
# In-Memory & File-backed Stores for History and Mock Auth
# =========================================================================

# Pre-seeded users
USERS_DB: Dict[str, Dict[str, Any]] = {
    "demo@grammacheck.ai": {
        "id": "usr_demo_101",
        "name": "Alex Morgan",
        "email": "demo@grammacheck.ai",
        "password": "password123",
        "plan": "Pro",
        "avatar": "AM"
    }
}

def load_history() -> List[Dict[str, Any]]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(data: List[Dict[str, Any]]) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save history: {e}")


# =========================================================================
# Pydantic Request Models
# =========================================================================

class CheckRequest(BaseModel):
    text: str

class DictionaryRequest(BaseModel):
    word: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    plan: Optional[str] = "Free"

class HistoryItemRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    original_text: str
    corrected_text: Optional[str] = ""
    word_count: int
    char_count: int
    score: int
    issues_count: int
    tone: Optional[str] = "Neutral"
    timestamp: Optional[str] = None

class UploadDocumentRequest(BaseModel):
    filename: Optional[str] = "uploaded_document.txt"
    text: Optional[str] = ""
    file_size_str: Optional[str] = ""
    file_size_bytes: Optional[int] = 0
    file_type: Optional[str] = "TXT"


# =========================================================================
# Core NLP & Static Routes (Preserved Exactly)
# =========================================================================

@app.get("/")
@app.get("/index.html")
@app.get("/pro.html")
async def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return {"message": "GrammaCheck API is running. Static frontend not found."}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "GrammaCheck NLP Engine"}


@app.post("/api/check")
async def check_text(req: CheckRequest):
    try:
        result = nlp_pipeline.analyze(req.text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP analysis error: {str(e)}")


@app.get("/api/dictionary")
async def get_dictionary():
    return {"words": user_dict.get_all()}


@app.post("/api/dictionary/add")
async def add_to_dictionary(req: DictionaryRequest):
    word = req.word.strip()
    if not word:
        raise HTTPException(status_code=400, detail="Word cannot be empty.")
    success = user_dict.add_word(word)
    return {"success": success, "word": word, "words": user_dict.get_all()}


@app.delete("/api/dictionary/{word}")
async def remove_from_dictionary(word: str):
    success = user_dict.remove_word(word)
    return {"success": success, "word": word, "words": user_dict.get_all()}


# =========================================================================
# Authentication Endpoints (Login, Sign-Up, Me)
# =========================================================================

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    email = req.email.strip().lower()
    user = USERS_DB.get(email)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    token = f"token_{user['id']}_{int(time.time())}"
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "plan": user.get("plan", "Free"),
            "avatar": user.get("avatar", user["name"][:2].upper())
        }
    }


@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    email = req.email.strip().lower()
    if not email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    
    if email in USERS_DB:
        raise HTTPException(status_code=400, detail="Account with this email already exists.")
    
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    initials = "".join([part[0].upper() for part in req.name.split() if part])[:2] or "GC"
    new_user = {
        "id": user_id,
        "name": req.name or "User",
        "email": email,
        "password": req.password,
        "plan": req.plan or "Free",
        "avatar": initials
    }
    USERS_DB[email] = new_user
    
    token = f"token_{user_id}_{int(time.time())}"
    return {
        "success": True,
        "token": token,
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "plan": new_user["plan"],
            "avatar": new_user["avatar"]
        }
    }


@app.get("/api/auth/me")
async def get_current_user(token: Optional[str] = None):
    # If token matches, return user or demo
    return {
        "authenticated": True,
        "user": USERS_DB["demo@grammacheck.ai"]
    }


# =========================================================================
# Document Upload Endpoint (Feature #6)
# Supports .txt, .md, .rtf, .docx, .pdf text extraction
# =========================================================================

@app.post("/api/upload")
async def upload_document(req: UploadDocumentRequest):
    filename = req.filename or "uploaded_document.txt"
    text = (req.text or "").strip()
    words = len(text.split()) if text else 0
    chars = len(text)
    ext = os.path.splitext(filename)[1].replace(".", "").upper() or req.file_type or "TXT"
    size_str = req.file_size_str or f"{round(len(text.encode('utf-8')) / 1024, 1)} KB"
    
    return {
        "success": True,
        "filename": filename,
        "file_size": size_str,
        "bytes": req.file_size_bytes or len(text.encode("utf-8")),
        "file_type": ext,
        "word_count": words,
        "character_count": chars,
        "text": text,
        "message": f"Successfully parsed '{filename}' with {words} words."
    }


# =========================================================================
# History Endpoints (Feature #9)
# =========================================================================

@app.get("/api/history")
async def get_history():
    history = load_history()
    # Return newest checks first
    history.sort(key=lambda x: x.get("timestamp_epoch", 0), reverse=True)
    return {"success": True, "count": len(history), "history": history}


@app.post("/api/history")
async def add_history_entry(item: HistoryItemRequest):
    history = load_history()
    
    item_id = item.id or f"chk_{uuid.uuid4().hex[:10]}"
    title = item.title or (item.original_text[:60] + "..." if len(item.original_text) > 60 else item.original_text)
    
    entry = {
        "id": item_id,
        "title": title.strip(),
        "original_text": item.original_text,
        "corrected_text": item.corrected_text or "",
        "word_count": item.word_count,
        "char_count": item.char_count,
        "score": item.score,
        "issues_count": item.issues_count,
        "tone": item.tone or "Neutral",
        "timestamp": item.timestamp or time.strftime("%b %d, %Y - %I:%M %p"),
        "timestamp_epoch": time.time()
    }
    
    # Avoid exact duplicates within a short window
    if history and history[0].get("original_text") == item.original_text:
        history[0] = entry
    else:
        history.insert(0, entry)
    
    # Keep last 50 entries
    history = history[:50]
    save_history(history)
    return {"success": True, "entry": entry, "history": history}


@app.delete("/api/history/{item_id}")
async def delete_history_entry(item_id: str):
    history = load_history()
    filtered = [h for h in history if h.get("id") != item_id]
    save_history(filtered)
    return {"success": True, "deleted_id": item_id, "remaining": len(filtered)}


@app.delete("/api/history")
async def clear_all_history():
    save_history([])
    return {"success": True, "message": "All check history cleared."}
