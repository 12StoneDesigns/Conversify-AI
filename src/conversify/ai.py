"""Main AI class that coordinates all components of the conversational system."""

import sys
import json
import pyfiglet
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from colorama import init, Fore, Style

from .nlp.language import LanguageModel
from .response.generator import ResponseGenerator
from .models.context import ConversationContext
from .models.profile import UserProfile
from .models.message import Message
from .utils.enums import ConversationState

# Initialize colorama and logging
init()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversifyAI:
    """Main class that coordinates the conversational AI system."""
    
    def __init__(self):
        """Initialize all components of the AI system."""
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
        """Run the main conversation loop."""
        # Display welcome message
        print(Fore.CYAN + pyfiglet.figlet_format("Conversify-AI", font="slant"))
        print(Fore.GREEN + "Welcome! Type '/help' for available commands or just start chatting!")
        print(Style.RESET_ALL)
        
        while True:
            try:
                # Get user input
                user_input = input(Fore.YELLOW + "You: " + Style.RESET_ALL)
                
                # Check for commands
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
        """Process a user message and generate a response."""
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
        
        # Set entities from intent and topics
        msg.entities = {
            'topics': msg.topics,
            **msg.intent.entities  # Include any entities from intent classification
        }
        
        # Update conversation state based on intent
        if msg.intent.primary == 'greeting':
            self.conversation_context.state = ConversationState.INITIAL
        elif msg.intent.primary == 'farewell':
            self.conversation_context.state = ConversationState.CONCLUDING
        elif msg.intent.primary in ['question', 'clarification']:
            self.conversation_context.state = ConversationState.ENGAGED
        elif msg.intent.primary in ['about', 'capabilities', 'help']:
            self.conversation_context.state = ConversationState.ENGAGED
        else:
            if self.conversation_context.state == ConversationState.INITIAL:
                self.conversation_context.state = ConversationState.ENGAGED
        
        # Update context and user profile
        self.conversation_context.add_message(msg)
        self.user_profile.update_from_message(msg)
        
        # Generate response
        response = await self.response_generator.generate_response(
            msg,
            self.conversation_context,
            self.user_profile
        )
        
        return response if isinstance(response, str) else "I'm sorry, I couldn't generate a response."
    
    async def show_help(self, *args) -> bool:
        """Display available commands."""
        print(Fore.CYAN + "\nAvailable Commands:")
        for cmd, func in self.commands.items():
            print(f"{cmd}: {func.__name__.replace('_', ' ')}")
        return True
    
    async def exit_chat(self, *args) -> bool:
        """Exit the chat gracefully."""
        print(Fore.YELLOW + "\nGoodbye! Have a great day!")
        sys.exit(0)
    
    async def show_topic_graph(self, *args) -> bool:
        """Display the topic relationship graph."""
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
        """Display conversation trends and analytics."""
        print(Fore.CYAN + "\nConversation Trends Analysis:")
        
        # Sentiment trends
        sentiment_trend = self.conversation_context.get_sentiment_trend()
        print(Fore.GREEN + "\nSentiment Trend:")
        trend_direction = "improving" if sentiment_trend > 0 else "declining" if sentiment_trend < 0 else "stable"
        print(f"Conversation tone is {trend_direction} (slope: {sentiment_trend:.3f})")
        
        return True
    
    async def export_user_profile(self, *args) -> bool:
        """Export the user profile to a JSON file."""
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
        """Generate a summary of the conversation."""
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
