"""Response templates and knowledge base for the ChatBot."""

RESPONSES = {
    "greeting": [
        "Hello! I'm ConversifyAI, a technical assistant. What would you like to discuss today?",
        "Hi there! I specialize in development topics. What can I help you with?",
        "Welcome! I'd love to help with your technical questions. What's on your mind?"
    ],
    "how_are_you": [
        "I'm running smoothly and ready to dive into technical discussions! What would you like to explore?",
        "I'm here and eager to help with your development questions! What are you working on?",
        "I'm operational and excited to discuss technology! What's your current project about?"
    ],
    "tech_stack": {
        "python_web": [
            "For Python web applications, I'd recommend considering:\n1. FastAPI - Great for high-performance APIs\n2. Django - Perfect for full-featured web apps\n3. Flask - Excellent for smaller projects\nWhat's your specific use case? That would help me provide more targeted recommendations.",
            "Python web development has several strong options:\n- FastAPI for modern, async-first applications\n- Django for enterprise-grade applications\n- Flask for lightweight, customizable solutions\nWhat kind of features do you need in your application?",
            "Some popular Python web stacks include:\n1. FastAPI + SQLAlchemy + Pydantic\n2. Django + DRF + Celery\n3. Flask + SQLAlchemy + Marshmallow\nWould you like to know more about any of these combinations?"
        ],
        "frontend": [
            "For frontend development, consider:\n1. React - Great ecosystem and job market\n2. Vue - Gentle learning curve\n3. Angular - Full-featured framework\nWhat's your experience level with frontend development?",
            "Modern frontend development often uses:\n- React with Next.js for SSR\n- Vue with Nuxt.js\n- Svelte for performance\nAre you looking to build something specific?"
        ],
        "database": [
            "For databases, consider your needs:\n1. PostgreSQL - Feature-rich relational DB\n2. MongoDB - Flexible document store\n3. Redis - Fast in-memory storage\nWhat kind of data are you working with?",
            "Database selection depends on requirements:\n- PostgreSQL for complex queries\n- MongoDB for flexible schemas\n- SQLite for lightweight apps\nWhat's your primary use case?"
        ]
    },
    "project_discussion": [
        "That's an interesting approach! Have you considered using design patterns like {pattern} for this?",
        "Great progress! For scaling this solution, you might want to look into {technology}.",
        "Interesting challenge! In similar cases, I've seen developers successfully use {solution}."
    ],
    "problem_solving": [
        "Let's break this down:\n1. What's the specific requirement?\n2. What solutions have you tried?\n3. Are there any performance constraints?",
        "To help better, could you tell me:\n1. Expected behavior\n2. Current behavior\n3. Any error messages?",
        "Let's solve this step by step. First, what's the main goal you're trying to achieve?"
    ],
    "best_practices": [
        "Some key best practices for this:\n1. Write testable code\n2. Use type hints\n3. Follow SOLID principles\nWould you like me to elaborate on any of these?",
        "Important considerations include:\n- Code maintainability\n- Performance optimization\n- Security best practices\nWhich aspect interests you most?",
        "Best practices I'd recommend:\n1. Proper error handling\n2. Comprehensive documentation\n3. Regular code reviews\nAre you following any specific development methodology?"
    ],
    "follow_up": [
        "How are you planning to implement that? I might have some suggestions.",
        "That's a solid approach! Have you considered any alternative solutions?",
        "Interesting! What made you choose this particular solution?"
    ]
}

TOPICS = {
    "web_frameworks": ["django", "flask", "fastapi", "pyramid", "aiohttp"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "sqlite"],
    "frontend": ["react", "vue", "angular", "svelte", "javascript", "typescript"],
    "deployment": ["docker", "kubernetes", "aws", "heroku", "nginx"],
    "testing": ["pytest", "unittest", "selenium", "cypress", "jest"],
    "architecture": ["microservices", "monolith", "serverless", "api", "rest"]
}

def get_topic_from_message(message: str) -> str:
    """Identify the technical topic in a message."""
    message_lower = message.lower()
    
    for topic, keywords in TOPICS.items():
        if any(keyword in message_lower for keyword in keywords):
            return topic
    
    return None
