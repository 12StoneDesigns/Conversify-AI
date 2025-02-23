"""Main FastAPI application module."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
from backend.app.chatbot_responses import RESPONSES, TOPICS, get_topic_from_message

class ChatBot:
    def __init__(self):
        self.conversation_history: Dict[str, List[dict]] = {}
        self.current_topics: Dict[str, str] = {}  # Track current topic per connection
        self.responses = RESPONSES
        self.topics = TOPICS

    def _analyze_message(self, message: str, connection_id: str) -> tuple[str, str]:
        """Analyze message content to determine appropriate response category and topic."""
        message_lower = message.lower()
        
        # Check for basic interactions first
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting", None
        elif "how are you" in message_lower:
            return "how_are_you", None
            
        # Check for technical topics
        topic = get_topic_from_message(message)
        if topic:
            self.current_topics[connection_id] = topic
            
            # Handle specific technical questions
            if "best" in message_lower and ("stack" in message_lower or "framework" in message_lower):
                if "python" in message_lower and "web" in message_lower:
                    return "tech_stack", "python_web"
                elif any(word in message_lower for word in ["frontend", "ui", "interface"]):
                    return "tech_stack", "frontend"
                elif any(word in message_lower for word in ["database", "db", "storage"]):
                    return "tech_stack", "database"
            
            return "best_practices", topic
            
        # Check for problem-solving scenarios
        if any(word in message_lower for word in ["help", "issue", "problem", "error", "bug"]):
            return "problem_solving", self.current_topics.get(connection_id)
            
        return None, self.current_topics.get(connection_id)

    def _get_contextual_response(self, message: str, connection_id: str) -> str:
        """Generate a response based on message content and conversation history."""
        message_type, topic = self._analyze_message(message, connection_id)
        
        # Handle tech stack specific responses
        if message_type == "tech_stack" and topic in self.responses["tech_stack"]:
            return random.choice(self.responses["tech_stack"][topic])
        
        # Handle general message types
        if message_type and message_type in self.responses:
            if isinstance(self.responses[message_type], list):
                return random.choice(self.responses[message_type])
            
        # Use conversation history for better context
        history = self.conversation_history.get(connection_id, [])
        if history:
            last_messages = history[-2:] if len(history) >= 2 else history
            
            # Check for ongoing technical discussion
            if topic:
                if any("best practices" in msg["content"].lower() for msg in last_messages):
                    return random.choice(self.responses["best_practices"])
                return random.choice(self.responses["project_discussion"]).format(
                    pattern="Repository Pattern" if "database" in topic else "Factory Pattern",
                    technology="Redis caching" if "database" in topic else "TypeScript",
                    solution="connection pooling" if "database" in topic else "async/await"
                )
            
            # If we're in a technical conversation but no specific topic
            if self.current_topics.get(connection_id):
                return random.choice(self.responses["follow_up"])
        
        # Default to problem-solving approach
        return random.choice(self.responses["problem_solving"])

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
        
        # Generate response
        response = self._get_contextual_response(message, connection_id)
        
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

from fastapi.responses import FileResponse

# Frontend paths
frontend_path = Path(__file__).parent.parent.parent / "frontend"
static_path = frontend_path

# Serve static files
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Serve HTML files directly
@app.get("/about")
async def serve_about():
    return FileResponse(str(frontend_path / "about.html"))

@app.get("/privacy")
async def serve_privacy():
    return FileResponse(str(frontend_path / "privacy.html"))

@app.get("/terms")
async def serve_terms():
    return FileResponse(str(frontend_path / "terms.html"))

# Home page and catch-all route
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if not full_path:  # Root path
        return FileResponse(str(frontend_path / "index.html"))
    
    # Serve the requested file if it exists
    file_path = frontend_path / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    
    # Otherwise serve index.html
    return FileResponse(str(frontend_path / "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
