# Conversify-AI

## Description

Conversify-AI is a real-time technical development assistant chatbot that helps developers with programming questions, tech stack decisions, and coding best practices. It provides contextual responses and maintains conversation history to offer more relevant technical guidance.

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **WebSocket**: Real-time bidirectional communication
- **Uvicorn**: Lightning-fast ASGI server
- **Python 3.8+**: Core programming language

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Native WebSocket implementation
- **Responsive Design**: Mobile-friendly interface

### Features
- Real-time chat with WebSocket communication
- Context-aware technical responses
- Topic-based conversation tracking
- Development best practices guidance
- Tech stack recommendations
- Error handling and logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/12stonedesigns/conversify-ai.git
cd conversify-ai
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python run_server.py
```

5. Access the application:
- Open http://localhost:8000 in your browser
- Start asking technical questions!

## Features

### Technical Expertise
- Web development guidance
- Framework recommendations
- Architecture decisions
- Best practices advice

### Real-time Communication
- Instant responses
- WebSocket-based chat
- Connection status monitoring
- Error handling

### User Interface
- Clean, modern design
- Mobile-responsive layout
- Interactive elements
- Technical feature showcase

## Development

### Project Structure
```
conversify-ai/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI server + chat logic
│       └── chatbot_responses.py  # Response system
├── frontend/
│   ├── index.html          # Main chat interface
│   ├── styles.css          # Design system
│   └── js/
│       └── app.js          # WebSocket client
├── requirements.txt        # Python dependencies
└── run_server.py          # Server startup script
```

### Requirements
- Python 3.8 or higher
- FastAPI
- Uvicorn
- WebSockets
- Modern web browser

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Repository

- GitHub: [https://github.com/12stonedesigns/conversify-ai](https://github.com/12stonedesigns/conversify-ai)

## Author

- **Name**: T. Landon Love
- **Company**: 12Stone Designs
- **Email**: [12stonedesigns@gmail.com](mailto:12stonedesigns@gmail.com)

## License

This project is licensed under the MIT License.
