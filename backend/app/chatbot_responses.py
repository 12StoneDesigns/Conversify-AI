"""Response templates and knowledge base for the ChatBot."""
from typing import Dict, List, Optional

class PersonalityTrait:
    def __init__(self, name: str, responses: Dict[str, List[str]]):
        self.name = name
        self.responses = responses

PERSONALITY = PersonalityTrait(
    "helpful_technical_expert",
    {
        "acknowledgment": [
            "I understand what you're saying about {topic}.",
            "That's an interesting point about {topic}.",
            "I see what you mean regarding {topic}.",
        ],
        "enthusiasm": [
            "That's fascinating! {response}",
            "What an interesting challenge! {response}",
            "This is a great topic to explore. {response}"
        ],
        "technical_depth": [
            "Let me elaborate on that - {response}",
            "To dive deeper into this - {response}",
            "Here's a more detailed explanation: {response}"
        ]
    }
)

CONVERSATION_STATES = {
    "initial": "starting_conversation",
    "exploring": "exploring_topic",
    "problem_solving": "solving_problem",
    "explaining": "providing_explanation",
    "concluding": "wrapping_up"
}

RESPONSES = {
    "greeting": [
        "Hello! I'm ConversifyAI, your technical assistant. I specialize in software development and architecture. What would you like to discuss?",
        "Hi there! I'm ConversifyAI, and I'm here to help with your development questions and technical challenges. What's on your mind?",
        "Welcome! I'm ConversifyAI, a technical assistant focused on helping you with software development and architecture. How can I assist you today?"
    ],
    "how_are_you": [
        "I'm functioning optimally and ready to dive into technical discussions! I've been processing some interesting development patterns lately. What would you like to explore?",
        "I'm running smoothly and keeping up with the latest tech trends. I'd love to hear about your current project or challenges.",
        "I'm operating at peak performance and excited to engage in technical discussions. What development topics interest you?"
    ],
    "tech_stack": {
        "microservices": [
            {
                "context": "scalability",
                "response": "For a scalable microservices architecture, here's a recommended tech stack:\n1. Backend Services: Go or Node.js for high-performance APIs\n2. Message Queue: Apache Kafka for reliable event streaming\n3. Container Orchestration: Kubernetes for scaling and management\n4. Database: MongoDB for flexibility or PostgreSQL with sharding\n5. API Gateway: Kong or Netflix Zuul\n\nWould you like me to elaborate on any of these components?"
            },
            {
                "context": "performance",
                "response": "For high-performance microservices, consider:\n1. Go (Golang) for CPU-intensive services\n2. Redis for caching and session management\n3. gRPC for efficient inter-service communication\n4. Envoy for service mesh and load balancing\n5. Prometheus & Grafana for monitoring\n\nWhat performance aspects are most critical for your architecture?"
            },
            {
                "context": "reliability",
                "response": "For reliable microservices architecture:\n1. Spring Boot with resilience patterns\n2. RabbitMQ for reliable messaging\n3. Consul for service discovery\n4. ELK Stack for centralized logging\n5. Circuit breakers with Hystrix\n\nWhat reliability requirements do you have?"
            }
        ],
        "python_web": [
            {
                "context": "general",
                "response": "For Python web development, let's consider your specific needs. FastAPI excels in building high-performance APIs with automatic OpenAPI documentation. Django provides a robust, batteries-included framework ideal for complex applications. Flask offers flexibility for smaller projects or microservices. What's your primary focus - rapid API development, full-featured applications, or lightweight services?"
            },
            {
                "context": "performance",
                "response": "If performance is crucial, I'd recommend FastAPI. It's built on Starlette and Pydantic, offering async support and impressive speed. It can handle high concurrency while maintaining type safety and automatic validation. Would you like to know more about optimizing Python web applications?"
            },
            {
                "context": "enterprise",
                "response": "For enterprise applications, Django stands out with its comprehensive ecosystem. It includes an admin interface, ORM, authentication, and security features out of the box. Combined with Django REST Framework, it's powerful for building scalable APIs. What enterprise features are most important for your project?"
            }
        ],
        "frontend": [
            {
                "context": "modern",
                "response": "Modern frontend development has evolved significantly. React with Next.js offers excellent SSR and static generation. Vue 3 with Composition API provides great reactivity. Svelte brings a compile-time approach for better performance. Are you prioritizing developer experience, performance, or specific features?"
            },
            {
                "context": "performance",
                "response": "For optimal frontend performance, consider using Svelte or solid.js. They offer compile-time optimizations and minimal runtime overhead. React with proper optimization (memo, useMemo, useCallback) is also strong. What performance metrics are you targeting?"
            }
        ],
        "database": [
            {
                "context": "scalability",
                "response": "For scalable database solutions, consider your data patterns. PostgreSQL handles complex queries and relationships excellently. MongoDB scales horizontally for document-based data. Redis is perfect for high-speed caching and real-time operations. What's your expected data volume and access patterns?"
            },
            {
                "context": "performance",
                "response": "Database performance often depends on usage patterns. PostgreSQL with proper indexing handles complex queries well. Redis excels at high-throughput, low-latency operations. What are your specific performance requirements?"
            }
        ]
    },
    "project_discussion": [
        {
            "context": "architecture",
            "response": "Looking at your approach, have you considered {pattern}? It could help with {benefit}. For example, {example}"
        },
        {
            "context": "scaling",
            "response": "For scaling this solution, {technology} could be valuable. It addresses {problem} by {solution}. Would you like to explore this approach?"
        }
    ],
    "problem_solving": [
        {
            "context": "error",
            "response": "Let's solve this systematically:\n1. Can you share the specific error message?\n2. What behavior were you expecting?\n3. What steps have you tried so far?\n\nThis will help me provide a more targeted solution."
        },
        {
            "context": "optimization",
            "response": "To optimize this effectively, let's consider:\n1. Current performance metrics\n2. Specific bottlenecks you've identified\n3. Resource constraints\n\nThis information will help us find the best optimization strategy."
        }
    ],
    "best_practices": [
        {
            "context": "code_quality",
            "response": "Here are some key best practices to consider:\n1. Write testable code - use dependency injection and clear interfaces\n2. Implement comprehensive error handling\n3. Follow SOLID principles for better maintainability\n\nWould you like me to elaborate on any of these aspects?"
        },
        {
            "context": "security",
            "response": "For security best practices:\n1. Input validation and sanitization\n2. Proper authentication and authorization\n3. Regular security audits and updates\n\nI can provide specific examples for any of these areas."
        }
    ]
}

TOPICS = {
    "web_frameworks": {
        "keywords": ["django", "flask", "fastapi", "pyramid", "aiohttp"],
        "related_concepts": ["mvc", "orm", "routing", "middleware", "templates"]
    },
    "databases": {
        "keywords": ["postgresql", "mysql", "mongodb", "redis", "sqlite"],
        "related_concepts": ["acid", "nosql", "indexing", "sharding", "replication"]
    },
    "frontend": {
        "keywords": ["react", "vue", "angular", "svelte", "javascript", "typescript"],
        "related_concepts": ["components", "state", "routing", "hooks", "virtual dom"]
    },
    "deployment": {
        "keywords": ["docker", "kubernetes", "aws", "heroku", "nginx"],
        "related_concepts": ["containers", "orchestration", "scaling", "load balancing"]
    },
    "testing": {
        "keywords": ["pytest", "unittest", "selenium", "cypress", "jest"],
        "related_concepts": ["mocking", "assertions", "coverage", "integration", "e2e"]
    },
    "architecture": {
        "keywords": ["microservices", "monolith", "serverless", "api", "rest", "tech stack", "architecture"],
        "related_concepts": ["scalability", "coupling", "cohesion", "patterns", "distributed", "service mesh", "container", "orchestration"]
    }
}

def analyze_technical_context(message: str, history: List[dict]) -> Dict[str, any]:
    """Analyze message and conversation history for technical context."""
    context = {
        "topics": [],
        "complexity_level": "basic",
        "conversation_state": CONVERSATION_STATES["initial"],
        "technical_focus": None
    }
    
    # Handle greeting
    if message.lower() == "greeting":
        return context

    # Analyze message complexity
    technical_terms = sum(1 for topic in TOPICS.values() 
                         for keyword in topic["keywords"] + topic["related_concepts"]
                         if keyword in message.lower())
    if technical_terms > 5:
        context["complexity_level"] = "advanced"
    elif technical_terms > 2:
        context["complexity_level"] = "intermediate"

    # Identify topics
    for topic, data in TOPICS.items():
        if any(keyword in message.lower() for keyword in data["keywords"]):
            context["topics"].append(topic)
        if any(concept in message.lower() for concept in data["related_concepts"]):
            if topic not in context["topics"]:
                context["topics"].append(topic)

    # Determine conversation state
    if history:
        if any("error" in msg["content"].lower() or "issue" in msg["content"].lower() 
               for msg in history[-2:]):
            context["conversation_state"] = CONVERSATION_STATES["problem_solving"]
        elif any("how" in msg["content"].lower() or "explain" in msg["content"].lower() 
                for msg in history[-2:]):
            context["conversation_state"] = CONVERSATION_STATES["explaining"]
    
    # Identify technical focus
    if "performance" in message.lower() or "optimization" in message.lower():
        context["technical_focus"] = "performance"
    elif "scale" in message.lower() or "growth" in message.lower():
        context["technical_focus"] = "scalability"
    elif "security" in message.lower() or "vulnerability" in message.lower():
        context["technical_focus"] = "security"

    return context

def get_contextual_response(message: str, history: List[dict], 
                          current_topic: Optional[str] = None) -> str:
    """Generate a contextually appropriate response based on message analysis."""
    context = analyze_technical_context(message, history)
    
    # Handle greeting
    if message.lower() == "greeting":
        return RESPONSES["greeting"][0]
    
    # Add personality to response
    def add_personality(response: str, topic: str = "") -> str:
        if context["complexity_level"] == "advanced":
            response = PERSONALITY.responses["technical_depth"][0].format(response=response)
        elif context["conversation_state"] == CONVERSATION_STATES["problem_solving"]:
            response = PERSONALITY.responses["acknowledgment"][0].format(topic=topic) + " " + response
        return response

    # Handle specific technical discussions
    if context["topics"]:
        topic = context["topics"][0]
        
        # Check for architecture/tech stack questions
        if "architecture" in context["topics"]:
            # If it's about microservices, use that specific response
            if any(word in message.lower() for word in ["microservice", "distributed", "service"]):
                response_obj = RESPONSES["tech_stack"]["microservices"][0]
                if context["technical_focus"]:
                    for resp in RESPONSES["tech_stack"]["microservices"]:
                        if resp["context"] == context["technical_focus"]:
                            response_obj = resp
                            break
                return add_personality(response_obj["response"], "architecture")
        
        # Handle other tech stack questions
        if topic in TOPICS and context["technical_focus"] and topic in RESPONSES["tech_stack"]:
            for response_obj in RESPONSES["tech_stack"][topic]:
                if response_obj["context"] == context["technical_focus"]:
                    return add_personality(response_obj["response"], topic)

    # Handle problem-solving scenarios
    if context["conversation_state"] == CONVERSATION_STATES["problem_solving"]:
        for response_obj in RESPONSES["problem_solving"]:
            if response_obj["context"] == "error":
                return add_personality(response_obj["response"])

    # Default to best practices with context
    if context["topics"]:
        return add_personality(RESPONSES["best_practices"][0]["response"], context["topics"][0])

    return RESPONSES["greeting"][0]
