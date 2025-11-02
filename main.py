# main.py - CCR stack glue (Claude + optional Cursor API) for Replit
import os
import asyncio
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="CCR Glue Service")

# === ENV / Secrets (set these in Replit Secrets, not in repo) ===
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")           # required
CLAUDE_API_URL = os.getenv("CLAUDE_API_URL") or "https://api.anthropic.com/v1/complete"  # replace if different
CURSOR_API_KEY = os.getenv("CURSOR_API_KEY")           # optional (if you will use Cursor API)
CURSOR_API_URL = os.getenv("CURSOR_API_URL")           # optional: Cursor API endpoint
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")        # optional CORS restrict

# Health
@app.get("/health")
async def health():
    return {"status": "ok", "mode": "CCR glue"}

# Simple model request proxy to Claude
class ModelRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 512
    model: Optional[str] = None  # let user override if needed

@app.post("/ai/claude")
async def call_claude(req: ModelRequest):
    if not CLAUDE_API_KEY:
        raise HTTPException(status_code=500, detail="CLAUDE_API_KEY not configured")
    headers = {"Authorization": f"Bearer {CLAUDE_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": req.model or "claude-2.1",   # adjust to your account's model name
        "prompt": req.prompt,
        "max_tokens": req.max_tokens
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(CLAUDE_API_URL, json=payload, headers=headers)
        try:
            r.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Upstream error: {r.text}") from e
        return r.json()

# Optional: call Cursor API (generic wrapper)
class CursorRequest(BaseModel):
    action: str
    payload: dict

@app.post("/cursor/action")
async def cursor_action(req: CursorRequest):
    if not CURSOR_API_KEY or not CURSOR_API_URL:
        raise HTTPException(status_code=400, detail="Cursor API not configured")
    headers = {"Authorization": f"Bearer {CURSOR_API_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(CURSOR_API_URL, json={"action": req.action, "payload": req.payload}, headers=headers)
        try:
            r.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Cursor error: {r.text}") from e
        return r.json()

# Quick-start local logs endpoint (safe)
@app.post("/debug/echo")
async def debug_echo(payload: dict):
    return {"echo": payload}

# Background task example (non-blocking)
@app.post("/background/test")
async def background_test(request: Request):
    async def worker(data):
        # lightweight simulated background job
        await asyncio.sleep(1)
        print("BG job processed:", data)
    body = await request.json()
    asyncio.create_task(worker(body))
    return {"status": "queued"}
