"""Message-related data models."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime

@dataclass
class MessageIntent:
    """Represents the intent of a message with confidence scores and entities."""
    primary: str
    confidence: float
    secondary: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        """Make MessageIntent hashable."""
        return hash((self.primary, self.confidence))
    
    def __eq__(self, other):
        """Define equality for MessageIntent."""
        if not isinstance(other, MessageIntent):
            return False
        return (self.primary == other.primary and 
                self.confidence == other.confidence)

@dataclass
class Message:
    """Represents a single message in the conversation with associated metadata."""
    role: str
    content: str
    timestamp: str
    message_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    intent: Optional[MessageIntent] = None
    sentiment: float = 0.0
    topics: List[str] = field(default_factory=list)
    embeddings: Optional[np.ndarray] = None
    references: List[str] = field(default_factory=list)
    context_id: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        """Make Message hashable using core attributes."""
        return hash((self.role, self.content, self.message_id))
    
    def __eq__(self, other):
        """Define equality for Message."""
        if not isinstance(other, Message):
            return False
        return (self.role == other.role and 
                self.content == other.content and 
                self.message_id == other.message_id)
    
    def to_dict(self):
        """Convert the message to a dictionary format."""
        data = asdict(self)
        data['embeddings'] = self.embeddings.tolist() if self.embeddings is not None else None
        return data
