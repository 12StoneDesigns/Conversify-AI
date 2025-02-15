from enum import Enum, auto

class ConversationState(Enum):
    """Enum representing different states of a conversation."""
    INITIAL = auto()
    ENGAGED = auto()
    CLARIFYING = auto()
    CONCLUDING = auto()
    IDLE = auto()
