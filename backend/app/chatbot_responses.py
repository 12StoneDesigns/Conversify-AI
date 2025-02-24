"""Production-ready chatbot responses with enhanced context management."""
from typing import Dict, List, Optional, Tuple
import logging
import json
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    GREETING = "greeting"
    TOPIC_DISCUSSION = "topic_discussion"
    DEEP_DIVE = "deep_dive"
    CLARIFICATION = "clarification"
    TRANSITION = "transition"

@dataclass
class Topic:
    name: str
    subtopics: List[str]
    related_topics: List[str]
    key_concepts: List[str]

class KnowledgeGraph:
    def __init__(self):
        self.topics = {
            "python": Topic(
                name="Python",
                subtopics=["web_frameworks", "data_science", "testing", "deployment"],
                related_topics=["backend_development", "api_design", "databases"],
                key_concepts=["OOP", "async programming", "package management"]
            ),
            "web_frameworks": Topic(
                name="Web Frameworks",
                subtopics=["django", "flask", "fastapi"],
                related_topics=["api_design", "databases", "authentication"],
                key_concepts=["MVC", "routing", "middleware", "ORM"]
            ),
            "data_science": Topic(
                name="Data Science",
                subtopics=["machine_learning", "data_analysis", "visualization"],
                related_topics=["statistics", "big_data", "ai"],
                key_concepts=["numpy", "pandas", "scikit-learn", "matplotlib"]
            )
        }

    def get_related_topics(self, topic: str) -> List[str]:
        """Get related topics for smooth transitions."""
        if topic in self.topics:
            return self.topics[topic].related_topics
        return []

    def get_subtopics(self, topic: str) -> List[str]:
        """Get subtopics for deeper discussion."""
        if topic in self.topics:
            return self.topics[topic].subtopics
        return []

class ChatEngine:
    def __init__(self):
        self.knowledge_base = {
            "python": {
                "frameworks": {
                    "django": {
                        "description": "Full-featured web framework with built-in admin, ORM, and authentication",
                        "use_cases": ["Large applications", "Content management systems", "Enterprise solutions"],
                        "features": ["Admin interface", "ORM", "Authentication", "Forms", "Security"]
                    },
                    "flask": {
                        "description": "Lightweight and flexible micro-framework",
                        "use_cases": ["Small to medium applications", "APIs", "Microservices"],
                        "features": ["Routing", "Template engine", "Development server", "Extensions"]
                    },
                    "fastapi": {
                        "description": "Modern, fast framework for building APIs with Python 3.6+",
                        "use_cases": ["High-performance APIs", "Real-time applications", "Microservices"],
                        "features": ["Async support", "Auto API docs", "Type hints", "Data validation"]
                    }
                },
                "web_development": {
                    "backend": ["Django", "Flask", "FastAPI", "Pyramid"],
                    "database": ["SQLAlchemy", "Django ORM", "Tortoise ORM"],
                    "testing": ["pytest", "unittest", "Robot Framework"],
                    "deployment": ["Docker", "Gunicorn", "uWSGI"]
                },
                "data_science": {
                    "libraries": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
                    "use_cases": ["Data analysis", "Machine learning", "Visualization"],
                    "frameworks": ["TensorFlow", "PyTorch", "Keras"]
                }
            }
        }
        self.conversation_history = {}
        self.knowledge_graph = KnowledgeGraph()
        self.session_states = {}
        self.current_topics = {}

    def get_response(self, message: str, session_id: str) -> str:
        """Generate a response based on the message and conversation history."""
        try:
            # Initialize or get session data
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
                self.session_states[session_id] = ConversationState.GREETING
                self.current_topics[session_id] = None

            # Add message to history
            self.conversation_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "content": message,
                "is_bot": False
            })

            # Analyze context and generate response
            response, new_state = self._analyze_and_respond(message, session_id)
            
            # Update conversation state
            self.session_states[session_id] = new_state

            # Add response to history
            self.conversation_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "content": response,
                "is_bot": True
            })

            # Keep history manageable
            if len(self.conversation_history[session_id]) > 20:
                self.conversation_history[session_id] = self.conversation_history[session_id][-20:]

            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an issue. Could you rephrase that?"

    def _analyze_and_respond(self, message: str, session_id: str) -> Tuple[str, ConversationState]:
        """Analyze message context and generate appropriate response."""
        message = message.lower()
        current_state = self.session_states[session_id]
        current_topic = self.current_topics[session_id]
        history = self.conversation_history[session_id]

        # Check for topic changes or continuity
        new_topic = self._detect_topic(message)
        if new_topic and new_topic != current_topic:
            self.current_topics[session_id] = new_topic
            return self._handle_topic_transition(new_topic, current_topic, session_id)

        # Generate response based on current state and context
        if current_state == ConversationState.GREETING:
            if any(word in message for word in ["hi", "hello", "hey", "greetings"]):
                return self._greeting_response(), ConversationState.TOPIC_DISCUSSION
            return self._topic_prompt(), ConversationState.TOPIC_DISCUSSION

        elif current_state == ConversationState.TOPIC_DISCUSSION:
            return self._handle_topic_discussion(message, session_id)

        elif current_state == ConversationState.DEEP_DIVE:
            return self._handle_deep_dive(message, session_id)

        return self._default_response(), ConversationState.TOPIC_DISCUSSION

    def _detect_topic(self, message: str) -> Optional[str]:
        """Detect the main topic from the message."""
        topics = {
            "python": ["python", "py", "pip"],
            "web_frameworks": ["framework", "django", "flask", "fastapi", "web"],
            "data_science": ["data", "analysis", "machine learning", "visualization"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message.lower() for keyword in keywords):
                return topic
        return None

    def _handle_topic_transition(self, new_topic: str, old_topic: Optional[str], session_id: str) -> Tuple[str, ConversationState]:
        """Handle smooth transition between topics."""
        if not old_topic:
            return self._generate_topic_introduction(new_topic), ConversationState.TOPIC_DISCUSSION

        related_topics = self.knowledge_graph.get_related_topics(old_topic)
        if new_topic in related_topics:
            return (
                f"While we're discussing {old_topic}, it's interesting to explore its connection with {new_topic}. "
                f"{self._generate_topic_introduction(new_topic)}",
                ConversationState.TOPIC_DISCUSSION
            )
        
        return (
            f"Let's switch gears and talk about {new_topic}. "
            f"{self._generate_topic_introduction(new_topic)}",
            ConversationState.TOPIC_DISCUSSION
        )

    def _generate_topic_introduction(self, topic: str) -> str:
        """Generate an introduction for a topic."""
        if topic == "python":
            return "Python is a versatile language used in web development, data science, and more. What aspect interests you most?"
        elif topic == "web_frameworks":
            return "Python offers several powerful web frameworks like Django, Flask, and FastAPI. Would you like to compare them or learn about a specific one?"
        elif topic == "data_science":
            return "Python is excellent for data science with libraries like NumPy, Pandas, and Scikit-learn. What kind of data analysis are you interested in?"
        return self._default_response()

    def _handle_topic_discussion(self, message: str, session_id: str) -> Tuple[str, ConversationState]:
        """Handle ongoing topic discussion with context awareness."""
        current_topic = self.current_topics[session_id]
        
        if not current_topic:
            return self._default_response(), ConversationState.TOPIC_DISCUSSION

        # Check for deep-dive indicators
        if any(word in message.lower() for word in ["how", "explain", "details", "example"]):
            return self._handle_deep_dive(message, session_id)

        # Generate contextual response based on topic
        if current_topic == "web_frameworks":
            if "compare" in message or "difference" in message:
                return self._compare_frameworks(), ConversationState.DEEP_DIVE
            elif any(fw in message for fw in ["django", "flask", "fastapi"]):
                framework = next(fw for fw in ["django", "flask", "fastapi"] if fw in message)
                return self._framework_info(framework), ConversationState.DEEP_DIVE

        elif current_topic == "data_science":
            return self._data_science_info(), ConversationState.DEEP_DIVE

        return self._generate_topic_introduction(current_topic), ConversationState.TOPIC_DISCUSSION

    def _handle_deep_dive(self, message: str, session_id: str) -> Tuple[str, ConversationState]:
        """Handle detailed technical discussions."""
        current_topic = self.current_topics[session_id]
        
        if not current_topic:
            return self._default_response(), ConversationState.TOPIC_DISCUSSION

        subtopics = self.knowledge_graph.get_subtopics(current_topic)
        
        # Generate detailed response with examples and explanations
        if current_topic == "web_frameworks":
            if "django" in message.lower():
                return (
                    "Django is a high-level framework that follows the MVT pattern. "
                    "Here's a quick example of a Django view:\n\n"
                    "```python\n"
                    "from django.shortcuts import render\n"
                    "def home(request):\n"
                    "    return render(request, 'home.html', {'message': 'Welcome'})\n"
                    "```\n\n"
                    "Would you like to know more about models, views, or templates?",
                    ConversationState.DEEP_DIVE
                )

        return (
            f"Let's explore {current_topic} in detail. "
            f"We can discuss: {', '.join(subtopics)}. "
            "What interests you most?",
            ConversationState.DEEP_DIVE
        )

    def _greeting_response(self) -> str:
        """Return a contextual greeting message."""
        return (
            "Hi! I'm here to help with technical topics. "
            "I specialize in Python web frameworks, data science, and development practices. "
            "What would you like to discuss?"
        )

    def _topic_prompt(self) -> str:
        """Prompt user to choose a topic."""
        return (
            "I can help you with:\n\n"
            "1. Python web frameworks (Django, Flask, FastAPI)\n"
            "2. Web development tools and practices\n"
            "3. Data science libraries and frameworks\n\n"
            "What would you like to explore?"
        )

    def _compare_frameworks(self) -> str:
        return """Here's a detailed comparison of Python web frameworks:

1. Django:
   - Full-featured framework with "batteries included"
   - Best for: Large applications, CMS, Enterprise solutions
   - Pros: Admin interface, ORM, authentication, forms
   - Cons: Steeper learning curve, might be overkill for small projects

2. Flask:
   - Lightweight and flexible micro-framework
   - Best for: Small to medium projects, APIs, Microservices
   - Pros: Simple to learn, highly extensible, minimal
   - Cons: Need to choose and configure extensions

3. FastAPI:
   - Modern, high-performance async framework
   - Best for: APIs, real-time applications, microservices
   - Pros: Async support, automatic docs, type validation
   - Cons: Newer ecosystem, primarily focused on APIs

Would you like to explore any specific framework in detail?"""

    def _framework_info(self, framework: str) -> str:
        info = self.knowledge_base["python"]["frameworks"][framework]
        return f"""{framework.title()}: {info['description']}

Best use cases:
{chr(10).join('- ' + case for case in info['use_cases'])}

Key features:
{chr(10).join('- ' + feature for feature in info['features'])}

Would you like to see some code examples or learn about specific features?"""

    def _data_science_info(self) -> str:
        data_info = self.knowledge_base["python"]["data_science"]
        return f"""Python's data science ecosystem includes powerful libraries:

Core Libraries:
{', '.join(data_info['libraries'])}

Common Applications:
{chr(10).join('- ' + use_case for use_case in data_info['use_cases'])}

Popular ML Frameworks:
{', '.join(data_info['frameworks'])}

Would you like to explore any specific library or use case?"""

    def _default_response(self) -> str:
        return """I can help you with:

1. Python web frameworks (Django, Flask, FastAPI)
2. Web development tools and practices
3. Data science libraries and frameworks

What aspect would you like to explore?"""

# Initialize global chat engine
chat_engine = ChatEngine()

def get_contextual_response(message: str, history: List[dict],
                          current_topic: Optional[str] = None) -> str:
    """Generate a contextually appropriate response."""
    # Use session ID based on history to maintain context
    session_id = str(hash(str(history[:2]))) if history else "default"
    return chat_engine.get_response(message, session_id)
