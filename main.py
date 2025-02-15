import pyfiglet
import itertools
import threading
import time
import sys
import json
import os
import re
import nltk
import numpy as np
import torch
import transformers
import logging
import asyncio
import aiohttp
import yaml
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style
from difflib import SequenceMatcher
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto

# Initialize colorama and logging
init()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer

class ConversationState(Enum):
    INITIAL = auto()
    ENGAGED = auto()
    CLARIFYING = auto()
    CONCLUDING = auto()
    IDLE = auto()

@dataclass
class MessageIntent:
    primary: str
    confidence: float
    secondary: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Message:
    role: str
    content: str
    timestamp: str
    message_id: str = field(default_factory=lambda: str(time.time()))
    intent: Optional[MessageIntent] = None
    sentiment: float = 0.0
    topics: List[str] = field(default_factory=list)
    embeddings: Optional[np.ndarray] = None
    references: List[str] = field(default_factory=list)
    context_id: Optional[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['embeddings'] = self.embeddings.tolist() if self.embeddings is not None else None
        return data

class NLP:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer()
        
    def analyze_sentiment(self, text: str) -> float:
        scores = self.sia.polarity_scores(text)
        return scores['compound']
    
    def extract_topics(self, text: str) -> List[str]:
        # Simple topic extraction using NLTK
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        topics = []
        
        # Extract nouns as topics
        for word, tag in tagged:
            if tag.startswith('NN'):  # Noun
                topics.append(word.lower())
                
        return list(set(topics))  # Remove duplicates

class LanguageModel:
    def __init__(self):
        self.tokenizer = transformers.AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = transformers.AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.nlp = NLP()
        self.intent_classifier = self._load_intent_classifier()
        self.intent_examples = {
            'greeting': ['hi there', 'hello', 'hey', 'good morning', 'greetings'],
            'farewell': ['goodbye', 'bye', 'see you later', 'farewell', 'have a good day'],
            'thank': ['thank you', 'thanks a lot', 'appreciate it', 'thanks for your help'],
            'help': ['can you help me', 'i need assistance', 'help please', 'support needed'],
            'about': ['tell me about yourself', 'who are you', 'what kind of bot are you', 'your background'],
            'capabilities': ['what can you do', 'show me your features', 'what are you capable of', 'your abilities'],
            'smalltalk': ['how are you', 'how are you doing', 'what\'s up', 'how\'s it going', 'what\'s new']
        }
        # Cache intent example embeddings
        self.intent_embeddings = self._cache_intent_embeddings()
        
    def _cache_intent_embeddings(self):
        intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            example_embeddings = []
            for example in examples:
                embedding = self.get_embeddings(example)
                example_embeddings.append(embedding)
            intent_embeddings[intent] = np.array(example_embeddings)
        return intent_embeddings
        
    def _load_intent_classifier(self):
        # Custom intent classification model
        intents_path = Path('data/intents.yaml')
        if intents_path.exists():
            with open(intents_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def get_embeddings(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()
    
    def classify_intent(self, text: str) -> MessageIntent:
        # Extract entities using NLTK
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        entities = nltk.chunk.ne_chunk(tagged)
        
        # Extract named entities
        extracted_entities = {}
        for node in entities:
            if hasattr(node, 'label'):
                entity_text = ' '.join([child[0] for child in node])
                extracted_entities[node.label()] = entity_text

        # Get embeddings for the input text
        text_embedding = self.get_embeddings(text).reshape(1, -1)

        # Calculate similarity scores for each intent using cached embeddings
        intent_scores = {}
        for intent, embeddings in self.intent_embeddings.items():
            # Calculate similarity with all examples of this intent
            similarities = cosine_similarity(text_embedding, embeddings).flatten()
            # Use max similarity as the score for this intent
            intent_scores[intent] = np.max(similarities)

        # Set confidence threshold
        confidence_threshold = 0.6  # Adjust this threshold as needed
        max_score = max(intent_scores.values())
        
        # Get primary intent
        primary_intent = ('unknown', 0.0)
        if max_score >= confidence_threshold:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Get secondary intents with confidence threshold
        secondary_intents = [
            intent for intent, score in intent_scores.items() 
            if score >= confidence_threshold * 0.8  # Slightly lower threshold for secondary intents
            and intent != primary_intent[0]
        ]
        
        return MessageIntent(
            primary=primary_intent[0],
            confidence=primary_intent[1],
            secondary=secondary_intents,
            entities=extracted_entities
        )

class ConversationContext:
    def __init__(self, max_size: int = 1000):
        self.messages: deque = deque(maxlen=max_size)
        self.state: ConversationState = ConversationState.INITIAL
        self.topic_graph: Dict[str, Set[str]] = defaultdict(set)
        self.sentiment_history: List[float] = []
        self.active_topics: Set[str] = set()
        self.last_update: datetime = datetime.now()
        
    def add_message(self, message: Message):
        self.messages.append(message)
        self.update_topic_graph(message)
        self.update_sentiment_history(message)
        self.last_update = datetime.now()
        
    def update_topic_graph(self, message: Message):
        for topic in message.topics:
            self.active_topics.add(topic)
            for other_topic in message.topics:
                if topic != other_topic:
                    self.topic_graph[topic].add(other_topic)
                    
    def update_sentiment_history(self, message: Message):
        self.sentiment_history.append(message.sentiment)
        if len(self.sentiment_history) > 100:
            self.sentiment_history.pop(0)
            
    def get_topic_relationships(self) -> Dict[str, List[str]]:
        return {topic: list(related) for topic, related in self.topic_graph.items()}
    
    def get_sentiment_trend(self) -> float:
        if len(self.sentiment_history) < 2:
            return 0.0
        return np.polyfit(range(len(self.sentiment_history)), self.sentiment_history, 1)[0]

class UserProfile:
    def __init__(self):
        self.interests: Dict[str, float] = defaultdict(float)
        self.interaction_patterns: Dict[str, Any] = defaultdict(int)
        self.sentiment_baseline: float = 0.0
        self.topic_preferences: Dict[str, float] = defaultdict(float)
        self.conversation_style: Dict[str, float] = defaultdict(float)
        self.response_history: Dict[str, List[str]] = defaultdict(list)
        self.engagement_metrics: Dict[str, float] = defaultdict(float)
        
    def update_from_message(self, message: Message):
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
                    
        # Update conversation style
        msg_length = len(message.content.split())
        self.conversation_style['avg_message_length'] = (
            (self.conversation_style.get('avg_message_length', 0) * self.conversation_style.get('message_count', 0) + msg_length) /
            (self.conversation_style.get('message_count', 0) + 1)
        )
        self.conversation_style['message_count'] = self.conversation_style.get('message_count', 0) + 1
        
    def get_preferred_topics(self, n: int = 5) -> List[Tuple[str, float]]:
        return sorted(self.topic_preferences.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def get_engagement_score(self) -> float:
        return np.mean(list(self.engagement_metrics.values())) if self.engagement_metrics else 0.0

class ResponseGenerator:
    def __init__(self, language_model: LanguageModel):
        self.language_model = language_model
        self.response_cache = LRUCache(maxsize=1000)
        self.template_engine = self._init_template_engine()
        self.conversation_strategies = self._load_strategies()
        
    def _init_template_engine(self):
        return {
            'default': yaml.safe_load(open('data/templates.yaml', 'r', encoding='utf-8')) if os.path.exists('data/templates.yaml') else {},
            'custom': {}
        }
    
    def _load_strategies(self):
        return {
            ConversationState.INITIAL: self._handle_initial_state,
            ConversationState.ENGAGED: self._handle_engaged_state,
            ConversationState.CLARIFYING: self._handle_clarifying_state,
            ConversationState.CONCLUDING: self._handle_concluding_state,
            ConversationState.IDLE: self._handle_idle_state
        }
    
    async def generate_response(self, 
                              message: Message,
                              context: ConversationContext,
                              user_profile: UserProfile,
                              mode: str = 'casual') -> str:
        # Check cache first
        cache_key = f"{message.content}:{mode}:{context.state.name}"
        if cached_response := self.response_cache.get(cache_key):
            return cached_response
        
        # Generate response based on conversation state
        strategy = self.conversation_strategies[context.state]
        response = await strategy(message, context, user_profile, mode)
        
        # Cache response
        self.response_cache[cache_key] = response
        return response
    
    async def _handle_initial_state(self, 
                                  message: Message,
                                  context: ConversationContext,
                                  user_profile: UserProfile,
                                  mode: str) -> str:
        templates = self.template_engine['default'].get(mode, self.template_engine['default'].get('casual', {}))
        
        if message.intent and message.intent.primary in templates:
            responses = templates[message.intent.primary]
            if responses:
                import random
                return random.choice(responses)
        
        # Fallback to time-based greeting
        hour = datetime.now().hour
        greeting = self._get_time_appropriate_greeting(hour, mode)
        
        # Add personalization if user has history
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
        templates = self.template_engine['default'].get(mode, self.template_engine['default'].get('casual', {}))
        
        # Try to use template based on intent
        if message.intent and message.intent.primary in templates:
            responses = templates[message.intent.primary]
            if responses:
                import random
                response = random.choice(responses)
                
                # Add contextual enhancement
                if context.get_sentiment_trend() > 0.1:
                    response += " 😊"
                elif context.get_sentiment_trend() < -0.1:
                    response += " 🤗"
                    
                return response
        
        # Fallback to generic response
        return "I understand. Please tell me more."
    
    async def _handle_clarifying_state(self,
                                     message: Message,
                                     context: ConversationContext,
                                     user_profile: UserProfile,
                                     mode: str) -> str:
        return "Could you please clarify what you mean?"
    
    async def _handle_concluding_state(self,
                                     message: Message,
                                     context: ConversationContext,
                                     user_profile: UserProfile,
                                     mode: str) -> str:
        return "It was great chatting with you! Have a wonderful day!"
    
    async def _handle_idle_state(self,
                                message: Message,
                                context: ConversationContext,
                                user_profile: UserProfile,
                                mode: str) -> str:
        return "I'm here if you'd like to continue our conversation."
    
    def _get_time_appropriate_greeting(self, hour: int, mode: str) -> str:
        greetings = {
            'casual': {
                'morning': "Good morning! 🌅",
                'afternoon': "Hey there! 🌞",
                'evening': "Good evening! 🌙",
                'night': "Hi! 🌟"
            },
            'professional': {
                'morning': "Good morning. I trust your day is starting well.",
                'afternoon': "Good afternoon. How may I assist you today?",
                'evening': "Good evening. I hope your day has been productive.",
                'night': "Greetings. How may I be of assistance?"
            },
            'creative': {
                'morning': "✨ As the sun paints the morning sky, welcome! 🌅",
                'afternoon': "🌟 Greetings on this sparkling afternoon! 🌞",
                'evening': "🌙 Welcome to this magical evening! ✨",
                'night': "🌠 The stars align for our conversation! ✨"
            }
        }
        
        time_of_day = (
            'morning' if 5 <= hour < 12
            else 'afternoon' if 12 <= hour < 17
            else 'evening' if 17 <= hour < 22
            else 'night'
        )
        
        return greetings.get(mode, greetings['casual'])[time_of_day]
    
    async def _generate_contextual_embedding(self,
                                          message: Message,
                                          history: List[Message],
                                          user_profile: UserProfile) -> np.ndarray:
        # Combine recent history with user preferences
        context_text = " ".join([msg.content for msg in history[-3:]])
        profile_text = " ".join([f"{topic} {score}" for topic, score in user_profile.interests.items()])
        
        # Generate embeddings
        with ThreadPoolExecutor() as executor:
            message_embedding = await asyncio.get_event_loop().run_in_executor(
                executor,
                self.language_model.get_embeddings,
                message.content
            )
            context_embedding = await asyncio.get_event_loop().run_in_executor(
                executor,
                self.language_model.get_embeddings,
                context_text
            )
            profile_embedding = await asyncio.get_event_loop().run_in_executor(
                executor,
                self.language_model.get_embeddings,
                profile_text
            )
        
        # Combine embeddings with weights
        return 0.5 * message_embedding + 0.3 * context_embedding + 0.2 * profile_embedding
    
    def _embedding_to_text(self, embedding: np.ndarray, mode: str) -> str:
        # This is a placeholder - in a real implementation, you would use a more sophisticated
        # method to convert embeddings back to text, possibly using a decoder model
        return "I understand what you're saying."
    
    def _enhance_response(self,
                         base_response: str,
                         intent: Optional[MessageIntent],
                         sentiment_trend: float,
                         user_profile: UserProfile) -> str:
        # Add context based on intent
        if intent and intent.primary != 'unknown':
            base_response += f" I sense that you're trying to {intent.primary}."
            
        # Add emotional context based on sentiment
        if sentiment_trend > 0.1:
            base_response += " I'm glad our conversation is going well!"
        elif sentiment_trend < -0.1:
            base_response += " I hope I can help improve your mood."
            
        return base_response

class StoneAI:
    def __init__(self):
        self.language_model = LanguageModel()
        self.response_generator = ResponseGenerator(self.language_model)
        self.conversation_context = ConversationContext()
        self.user_profile = UserProfile()
        
        # Initialize commands
        self.commands = {
            '/help': self.show_help,
            '/exit': self.exit_chat,
            '/topics': self.show_topic_graph,
            '/trends': self.show_trends,
            '/export': self.export_user_profile,
            '/summarize': self.summarize_conversation
        }
        
    async def run(self):
        # Display welcome message
        print(Fore.CYAN + pyfiglet.figlet_format("Conversify-AI", font="slant"))
        print(Fore.GREEN + "Welcome! Type '/help' for available commands or just start chatting!")
        print(Style.RESET_ALL)
        
        while True:
            try:
                # Get user input
                user_input = input(Fore.YELLOW + "You: " + Style.RESET_ALL)
                
                # Check for commands and ensure user input is a string
                if isinstance(user_input, str) and user_input.startswith('/'):
                    command = user_input.split()[0]
                    args = user_input.split()[1:] if len(user_input.split()) > 1 else []
                    
                    if command in self.commands:
                        await self.commands[command](*args)
                        continue
                    else:
                        print(Fore.RED + "Unknown command. Type '/help' for available commands.")
                        continue
                
                # Process regular message
                response = await self.process_message(user_input)
                print(Fore.GREEN + "AI: " + Style.RESET_ALL + response)
            
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nExiting gracefully...")
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                print(Fore.RED + "An error occurred. Please try again.")
                
    async def process_message(self, message: str) -> str:
        # Create message object with NLP analysis
        msg = Message(
            role='user',
            content=message,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Enhance message with NLP
        msg.intent = self.language_model.classify_intent(message)
        msg.sentiment = self.language_model.nlp.analyze_sentiment(message)
        msg.topics = self.language_model.nlp.extract_topics(message)
        msg.embeddings = self.language_model.get_embeddings(message)
        
        # Update conversation state based on intent
        if msg.intent.primary == 'greeting':
            self.conversation_context.state = ConversationState.INITIAL
        elif msg.intent.primary == 'farewell':
            self.conversation_context.state = ConversationState.CONCLUDING
        elif msg.intent.primary == 'about':
            self.conversation_context.state = ConversationState.ENGAGED
        elif msg.intent.primary in ['help', 'capabilities']:
            self.conversation_context.state = ConversationState.ENGAGED
        else:
            if self.conversation_context.state == ConversationState.INITIAL:
                self.conversation_context.state = ConversationState.ENGAGED
        
        # Update context and user profile
        self.conversation_context.add_message(msg)
        self.user_profile.update_from_message(msg)
        
        # Generate response and ensure it is a string
        response = await self.response_generator.generate_response(
            msg,
            self.conversation_context,
            self.user_profile
        )
        if not isinstance(response, str):
            response = "I'm sorry, I couldn't generate a response."
        
        return response
    
    async def show_help(self, *args) -> bool:
        print(Fore.CYAN + "\nAvailable Commands:")
        for cmd, func in self.commands.items():
            print(f"{cmd}: {func.__name__.replace('_', ' ')}")
        return True
    
    async def exit_chat(self, *args) -> bool:
        print(Fore.YELLOW + "\nGoodbye! Have a great day!")
        sys.exit(0)
    
    async def show_topic_graph(self, *args) -> bool:
        print(Fore.CYAN + "\nTopic Relationship Analysis:")
        
        relationships = self.conversation_context.get_topic_relationships()
        if not relationships:
            print(Fore.RED + "No topic relationships detected yet.")
            return True
            
        # Display topic clusters
        for topic, related in relationships.items():
            if related:
                print(Fore.GREEN + f"\n{topic}:")
                for related_topic in related:
                    print(Fore.WHITE + f"  └─ {related_topic}")
        
        return True
    
    async def show_trends(self, *args) -> bool:
        print(Fore.CYAN + "\nConversation Trends Analysis:")
        
        # Sentiment trends
        sentiment_trend = self.conversation_context.get_sentiment_trend()
        print(Fore.GREEN + "\nSentiment Trend:")
        trend_direction = "improving" if sentiment_trend > 0 else "declining" if sentiment_trend < 0 else "stable"
        print(f"Conversation tone is {trend_direction} (slope: {sentiment_trend:.3f})")
        
        return True
    
    async def export_user_profile(self, *args) -> bool:
        print(Fore.CYAN + "\nExporting User Profile...")
        
        export_data = {
            'interests': dict(self.user_profile.interests),
            'topic_preferences': dict(self.user_profile.topic_preferences),
            'conversation_style': dict(self.user_profile.conversation_style),
            'engagement_metrics': dict(self.user_profile.engagement_metrics),
            'interaction_patterns': dict(self.user_profile.interaction_patterns)
        }
        
        filename = f"user_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(Fore.GREEN + f"Profile exported to {filename}")
        return True
    
    async def summarize_conversation(self, *args) -> bool:
        print(Fore.CYAN + "\nGenerating Conversation Summary...")
        
        messages = list(self.conversation_context.messages)
        if not messages:
            print(Fore.RED + "No conversation to summarize.")
            return True
            
        # Group messages by topic
        topic_messages = defaultdict(list)
        for msg in messages:
            for topic in msg.topics:
                topic_messages[topic].append(msg.content)
                
        # Show summaries
        print(Fore.GREEN + "\nKey Discussion Points:")
        for topic, msgs in topic_messages.items():
            print(f"\n{topic}:")
            print(f"└─ {len(msgs)} messages")
            
        # Show interaction statistics
        total_duration = (float(messages[-1].message_id) - float(messages[0].message_id)) / 60
        print(Fore.GREEN + f"\nConversation Statistics:")
        print(f"Duration: {total_duration:.1f} minutes")
        print(f"Messages: {len(messages)}")
        print(f"Topics Covered: {len(topic_messages)}")
        
        return True

class LRUCache:
    def __init__(self, maxsize: int = 100):
        self.cache = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
        
    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            self.hits += 1
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        self.misses += 1
        return None
        
    def put(self, key: str, value: str):
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.maxsize:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
        
    def __setitem__(self, key: str, value: str):
        self.put(key, value)
        
    def __getitem__(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
        
    def get_stats(self) -> Dict[str, float]:
        total = self.hits + self.misses
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total if total > 0 else 0
        }

if __name__ == "__main__":
    try:
        ai = StoneAI()
        asyncio.run(ai.run())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nExiting gracefully...")
