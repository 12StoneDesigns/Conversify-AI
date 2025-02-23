"""
Simple server runner for ConversifyAI.
This script starts the FastAPI server which serves both the API and frontend.
"""
import uvicorn
import webbrowser
import time
from pathlib import Path
import os

def main():
    """Start the ConversifyAI server and open the web interface."""
    print("Starting ConversifyAI...")
    print("\nServer Information:")
    print("- Web Interface: http://localhost:8000")
    print("- WebSocket: ws://localhost:8000/ws/chat")
    
    # Ensure we're in the correct directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Open the web interface after a short delay
    def open_browser():
        time.sleep(2)  # Give the server time to start
        webbrowser.open("http://localhost:8000")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the server
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend", "frontend"]
    )

if __name__ == "__main__":
    main()
