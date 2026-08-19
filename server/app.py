import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api.routes import health, chat, voice, memory, tools, modes, knowledge
from server.api import websocket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("server.app")

app = FastAPI(
    title="NEUROCORE Core API Gateway",
    description="Unified local-first REST & WebSocket API for NEUROCORE multimodal AI agent platform.",
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local web interface & Tauri desktop app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(memory.router)
app.include_router(knowledge.router)
app.include_router(tools.router)
app.include_router(modes.router)
app.include_router(websocket.router)

@app.on_event("startup")
def startup_event():
    logger.info("NEUROCORE FastAPI Gateway Server starting up...")
    logger.info("Documentation available at http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)
