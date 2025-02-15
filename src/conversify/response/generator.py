"""Response generation system."""

import os
import yaml
import random
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from functools import lru_cache

from ..models.message import Message
from ..models.context import ConversationContext
from ..models.profile import UserProfile
from ..utils.enums import ConversationState
from ..nlp.language import LanguageModel

class ResponseGenerator:
    """Generates contextually appropriate responses with optimized performance."""
    
    def __init__(self, language_model: LanguageModel):
        """Initialize the response generator with optimizations."""
        self.language_model = language_model
        self.template_cache = {}
        self.last_topic = None
        self.user_name = None
        self._init_optimized_components()
        
    def _init_optimized_components(self):
        """Initialize components with optimizations."""
        self.template_engine = self._init_template_engine()
        self.conversation_strategies = {
            ConversationState.INITIAL: self._handle_initial_state,
            ConversationState.ENGAGED: self._handle_engaged_state,
            ConversationState.CLARIFYING: self._handle_clarifying_state,
            ConversationState.CONCLUDING: self._handle_concluding_state,
            ConversationState.IDLE: self._handle_idle_state
        }
        
        # Initialize common responses
        self.smalltalk_responses = {
            "whats up": ["Not much, just here to chat! How are you?", 
                        "Just helping out! What's on your mind?",
                        "All good here! What can I help you with?"],
            "how are you": ["I'm doing great, thanks for asking! How about you?",
                           "I'm good! How's your day going?",
                           "Doing well! What's new with you?"],
            "hello": ["Hi there! How can I help you today?",
                     "Hello! What's on your mind?",
                     "Hey! How can I assist you?"],
            "hi": ["Hi! How are you today?",
                  "Hello there! What can I help you with?",
                  "Hey! What's on your mind?"]
        }
        
    @lru_cache(maxsize=1)
    def _init_template_engine(self) -> Dict:
        """Initialize template engine with caching."""
        templates_path = 'config/templates.yaml'
        if os.path.exists(templates_path):
            with open(templates_path, 'r', encoding='utf-8') as f:
                return {'default': yaml.safe_load(f)}
        return {'default': {}}
    
    async def generate_response(self, 
                              message: Message,
                              context: ConversationContext,
                              user_profile: UserProfile,
                              mode: str = 'casual') -> str:
        """Generate optimized response based on current state and context."""
        try:
            # Check for name introduction
            if "my name is" in message.content.lower():
                name = message.content.lower().split("my name is")[-1].strip()
                self.user_name = name.title()
                return f"Nice to meet you, {self.user_name}! How can I help you today?"
            
            # Check for smalltalk
            lower_content = message.content.lower()
            for key, responses in self.smalltalk_responses.items():
                if key in lower_content:
                    return random.choice(responses)
            
            # Get appropriate strategy
            strategy = self.conversation_strategies[context.state]
            
            # Generate response
            response = await strategy(message, context, user_profile, mode)
            
            # Add name personalization if available
            if self.user_name and random.random() < 0.3:  # 30% chance to use name
                response = response.replace("you", f"you, {self.user_name}")
            
            return response
            
        except Exception as e:
            return "I'm here to help! What would you like to know?"
    
    async def _handle_initial_state(self, 
                                  message: Message,
                                  context: ConversationContext,
                                  user_profile: UserProfile,
                                  mode: str) -> str:
        """Handle initial state with optimizations."""
        templates = self.template_engine['default'].get(mode, {})
        
        if message.intent and message.intent.primary in templates:
            responses = templates[message.intent.primary]
            if responses:
                return random.choice(responses)
        
        # Quick time-based greeting
        hour = datetime.now().hour
        greeting = self._get_time_appropriate_greeting(hour, mode)
        
        # Add personalization if available
        if user_profile.interaction_patterns:
            preferred_topics = user_profile.get_preferred_topics(1)
            if preferred_topics:
                topic, _ = preferred_topics[0]
                greeting += f" I remember you're interested in {topic}!"
                
        return greeting
    
    async def _handle_engaged_state(self,
                                  message: Message,
                                  context: ConversationContext,
                                  user_profile: UserProfile,
                                  mode: str) -> str:
        """Handle engaged state with optimizations."""
        templates = self.template_engine['default'].get(mode, {})
        
        # Quick intent-based response
        if message.intent and message.intent.primary in ['question', 'clarification']:
            if self.last_topic:
                return f"What would you like to know about {self.last_topic}?"
        
        # Template-based response
        if message.intent and message.intent.primary in templates:
            responses = templates[message.intent.primary]
            if responses:
                response = random.choice(responses)
                self.last_topic = message.intent.primary
                return response
        
        # Entity-based response
        if message.entities and 'topics' in message.entities:
            topics = message.entities['topics']
            if topics:
                self.last_topic = topics[0]
                return "What's on your mind? I'm here to chat about anything!"
        
        return "I'm here to chat! What's on your mind?"
    
    async def _handle_clarifying_state(self,
                                     message: Message,
                                     context: ConversationContext,
                                     user_profile: UserProfile,
                                     mode: str) -> str:
        """Handle clarifying state with optimization."""
        return "Could you tell me more about what you mean?"
    
    async def _handle_concluding_state(self,
                                     message: Message,
                                     context: ConversationContext,
                                     user_profile: UserProfile,
                                     mode: str) -> str:
        """Handle concluding state with optimization."""
        self.last_topic = None
        return "Goodbye! Have a great day!"
    
    async def _handle_idle_state(self,
                                message: Message,
                                context: ConversationContext,
                                user_profile: UserProfile,
                                mode: str) -> str:
        """Handle idle state with optimization."""
        return "I'm here if you'd like to continue our chat!"
    
    @lru_cache(maxsize=24)  # Cache for each hour
    def _get_time_appropriate_greeting(self, hour: int, mode: str) -> str:
        """Get optimized time-based greeting."""
        greetings = {
            'casual': {
                'morning': "Good morning! How can I help?",
                'afternoon': "Hey there! What's on your mind?",
                'evening': "Good evening! How can I assist you?",
                'night': "Hi! What can I help you with?"
            },
            'professional': {
                'morning': "Good morning. How may I assist you?",
                'afternoon': "Good afternoon. How can I help?",
                'evening': "Good evening. What can I do for you?",
                'night': "Hello. How may I help you?"
            }
        }
        
        time_of_day = (
            'morning' if 5 <= hour < 12
            else 'afternoon' if 12 <= hour < 17
            else 'evening' if 17 <= hour < 22
            else 'night'
        )
        
        return greetings.get(mode, greetings['casual'])[time_of_day]
