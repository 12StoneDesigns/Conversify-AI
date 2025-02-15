"""User profile management."""

from collections import defaultdict
from typing import Dict, List, Tuple, Any
from datetime import datetime
import numpy as np

from .message import Message

class UserProfile:
    """Manages and updates user profile information based on conversation history."""
    
    def __init__(self):
        self.interests: Dict[str, float] = defaultdict(float)
        self.interaction_patterns: Dict[str, Any] = defaultdict(int)
        self.sentiment_baseline: float = 0.0
        self.topic_preferences: Dict[str, float] = defaultdict(float)
        self.conversation_style: Dict[str, float] = defaultdict(float)
        self.response_history: Dict[str, List[str]] = defaultdict(list)
        self.engagement_metrics: Dict[str, float] = defaultdict(float)
        
    def update_from_message(self, message: Message):
        """Update profile based on a new message."""
        # Update interests based on topics
        for topic in message.topics:
            self.interests[topic] += 1.0
            
        # Update interaction patterns
        hour = datetime.fromtimestamp(float(message.message_id)).hour
        self.interaction_patterns[f"hour_{hour}"] += 1
        
        # Update topic preferences
        if message.intent:
            for topic in message.topics:
                if message.intent.primary in ['like', 'prefer', 'enjoy']:
                    self.topic_preferences[topic] += 1.0
                elif message.intent.primary in ['dislike', 'hate', 'avoid']:
                    self.topic_preferences[topic] -= 1.0
                    
        # Update conversation style metrics
        msg_length = len(message.content.split())
        self.conversation_style['avg_message_length'] = (
            (self.conversation_style.get('avg_message_length', 0) * 
             self.conversation_style.get('message_count', 0) + msg_length) /
            (self.conversation_style.get('message_count', 0) + 1)
        )
        self.conversation_style['message_count'] = self.conversation_style.get('message_count', 0) + 1
        
    def get_preferred_topics(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get the user's n most preferred topics with their scores."""
        return sorted(self.topic_preferences.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def get_engagement_score(self) -> float:
        """Calculate overall engagement score based on various metrics."""
        return np.mean(list(self.engagement_metrics.values())) if self.engagement_metrics else 0.0
