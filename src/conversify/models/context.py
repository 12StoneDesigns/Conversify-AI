"""Conversation context management."""

from collections import deque, defaultdict
from typing import Dict, List, Set, Optional
from datetime import datetime
import numpy as np

from ..utils.enums import ConversationState
from .message import Message

class ConversationContext:
    """Manages the context and state of a conversation."""
    
    def __init__(self, max_size: int = 1000):
        self.messages: deque = deque(maxlen=max_size)
        self.state: ConversationState = ConversationState.INITIAL
        self.topic_graph: Dict[str, Set[str]] = defaultdict(set)
        self.sentiment_history: List[float] = []
        self.active_topics: Set[str] = set()
        self.last_update: datetime = datetime.now()
        
    def add_message(self, message: Message):
        """Add a new message to the conversation context."""
        self.messages.append(message)
        self.update_topic_graph(message)
        self.update_sentiment_history(message)
        self.last_update = datetime.now()
        
    def update_topic_graph(self, message: Message):
        """Update the topic relationship graph with new message topics."""
        for topic in message.topics:
            self.active_topics.add(topic)
            for other_topic in message.topics:
                if topic != other_topic:
                    self.topic_graph[topic].add(other_topic)
                    
    def update_sentiment_history(self, message: Message):
        """Update the sentiment history with the new message's sentiment."""
        self.sentiment_history.append(message.sentiment)
        if len(self.sentiment_history) > 100:
            self.sentiment_history.pop(0)
            
    def get_topic_relationships(self) -> Dict[str, List[str]]:
        """Get the relationships between topics in the conversation."""
        return {topic: list(related) for topic, related in self.topic_graph.items()}
    
    def get_sentiment_trend(self) -> float:
        """Calculate the trend in sentiment over recent messages."""
        if len(self.sentiment_history) < 2:
            return 0.0
        return np.polyfit(range(len(self.sentiment_history)), self.sentiment_history, 1)[0]
