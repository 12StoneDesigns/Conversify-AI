"""Language model for intent classification and text embeddings."""

from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

from .processor import NLP
from ..models.message import MessageIntent

class LanguageModel:
    """Handles intent classification and text embeddings using transformer models."""
    
    def __init__(self):
        """Initialize the language model components with optimizations."""
        # Initialize with optimizations
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Use a smaller, faster model
        model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        ).to(self.device)
        
        # Initialize NLP processor
        self.nlp = NLP()
        
        # Load intent classifier and examples
        self.intent_classifier = self._load_intent_classifier()
        self.intent_examples = {
            'greeting': ['hi', 'hello', 'hey'],
            'farewell': ['bye', 'goodbye', 'see you'],
            'thank': ['thanks', 'thank you'],
            'help': ['help', 'assist', 'support'],
            'about': ['who are you', 'what are you'],
            'capabilities': ['what can you do', 'features'],
            'question': ['what', 'how', 'why', 'when', 'where'],
            'clarification': ['explain', 'clarify', 'mean']
        }
        
        # Cache intent embeddings
        self.intent_embeddings = self._cache_intent_embeddings()
        
        # Warm up the model
        self._warm_up()
        
    def _warm_up(self):
        """Warm up the model with dummy input."""
        dummy_text = "hello world"
        self.get_embeddings(dummy_text)
        
    @lru_cache(maxsize=1000)
    def _cache_intent_embeddings(self) -> Dict[str, np.ndarray]:
        """Cache embeddings for all intent examples with optimization."""
        intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            # Batch process examples
            inputs = self.tokenizer(
                examples,
                padding=True,
                truncation=True,
                return_tensors='pt'
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling
                attention_mask = inputs['attention_mask']
                token_embeddings = outputs.last_hidden_state
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                intent_embeddings[intent] = embeddings.cpu().numpy()
                
        return intent_embeddings
        
    def _load_intent_classifier(self) -> Dict:
        """Load intent classification rules from YAML configuration."""
        intents_path = Path('config/intents.yaml')
        if intents_path.exists():
            with open(intents_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    @lru_cache(maxsize=1000)
    def get_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for the given text with caching."""
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            return_tensors='pt'
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Mean pooling with optimization
            attention_mask = inputs['attention_mask']
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            return embeddings.cpu().numpy()
    
    def classify_intent(self, text: str) -> MessageIntent:
        """Classify the intent of the given text with optimizations."""
        # Get embeddings for the input text
        text_embedding = self.get_embeddings(text)
        
        # Calculate similarity scores efficiently
        intent_scores = {}
        for intent, embeddings in self.intent_embeddings.items():
            similarities = cosine_similarity(text_embedding, embeddings)
            intent_scores[intent] = np.max(similarities)
        
        # Optimized thresholding
        confidence_threshold = 0.6
        max_score = max(intent_scores.values())
        
        # Get primary intent
        primary_intent = ('unknown', 0.0)
        if max_score >= confidence_threshold:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Get secondary intents efficiently
        secondary_threshold = confidence_threshold * 0.8
        secondary_intents = [
            intent for intent, score in intent_scores.items() 
            if score >= secondary_threshold and intent != primary_intent[0]
        ]
        
        # Perform text analysis with optimized NLP processor
        analysis = self.nlp.analyze_text(text)
        
        return MessageIntent(
            primary=primary_intent[0],
            confidence=primary_intent[1],
            secondary=secondary_intents,
            entities={
                'named_entities': analysis['entities'],
                'topics': [topic for topic, _ in analysis['topics']],
                'topic_scores': dict(analysis['topics']),
                'sentiment': analysis['sentiment']
            }
        )
