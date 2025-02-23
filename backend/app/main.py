"""Main FastAPI application module."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json
import random
import logging
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import chatbot responses
from backend.app.chatbot_responses import RESPONSES, TOPICS, get_contextual_response

class ChatBot:
    def __init__(self):
        self.conversation_history: Dict[str, List[dict]] = {}
        self.current_topics: Dict[str, str] = {}  # Track current topic per connection
        self.responses = RESPONSES
        self.topics = TOPICS

    def add_to_history(self, connection_id: str, message: str, is_bot: bool = False):
        """Add a message to the conversation history."""
        if connection_id not in self.conversation_history:
            self.conversation_history[connection_id] = []
        
        self.conversation_history[connection_id].append({
            "timestamp": datetime.now().isoformat(),
            "content": message,
            "is_bot": is_bot
        })
        
        # Keep only last 10 messages
        if len(self.conversation_history[connection_id]) > 10:
            self.conversation_history[connection_id] = self.conversation_history[connection_id][-10:]

    def get_response(self, message: str, connection_id: str) -> str:
        """Generate a response based on the input message and conversation history."""
        # Add user message to history
        self.add_to_history(connection_id, message)
        
        # Generate response using the new contextual system
        response = get_contextual_response(
            message, 
            self.conversation_history.get(connection_id, []),
            self.current_topics.get(connection_id)
        )
        
        # Add bot response to history
        self.add_to_history(connection_id, response, is_bot=True)
        
        return response

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = ChatBot()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        connection_id = f"conn_{len(self.active_connections) + 1}_{datetime.now().timestamp()}"
        self.active_connections[connection_id] = websocket
        logger.info(f"New WebSocket connection accepted: {connection_id}")
        return connection_id

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket connection removed: {connection_id}")

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from {connection_id}: {data}")
            
            try:
                message = json.loads(data)
                response = chatbot.get_response(message["content"], connection_id)
                await websocket.send_json({
                    "type": "message",
                    "content": response
                })
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "content": "I apologize, but I'm having trouble understanding. Could you rephrase that?"
                })
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(connection_id)

# API routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}

@app.get("/api/chat")
async def chat_http(message: str = Query(..., description="Message to send to the chatbot")):
    """HTTP endpoint for chat when WebSocket is not available."""
    try:
        response = chatbot.get_response(message, "http")
        return {"type": "message", "content": response}
    except Exception as e:
        logger.error(f"Error processing HTTP chat message: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "type": "error",
                "content": "I apologize, but I'm having trouble understanding. Could you rephrase that?"
            }
        )

from fastapi.staticfiles import StaticFiles

# Frontend paths
frontend_path = Path(__file__).parent.parent.parent / "frontend"

# Mount static files
app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="javascript")
app.mount("/styles", StaticFiles(directory=str(frontend_path / "styles")), name="styles")

# Serve HTML files directly
@app.get("/")
async def serve_index():
    """Serve the index page."""
    return FileResponse(str(frontend_path / "index.html"))

@app.get("/about")
async def serve_about():
    """Serve the about page."""
    return FileResponse(str(frontend_path / "about.html"))

@app.get("/privacy")
async def serve_privacy():
    """Serve the privacy policy page."""
    return FileResponse(str(frontend_path / "privacy.html"))

@app.get("/terms")
async def serve_terms():
    """Serve the terms of service page."""
    return FileResponse(str(frontend_path / "terms.html"))

# Catch-all route for other static files
@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    """Serve static files or return index.html for client-side routing."""
    file_path = frontend_path / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return FileResponse(str(frontend_path / "index.html"))
