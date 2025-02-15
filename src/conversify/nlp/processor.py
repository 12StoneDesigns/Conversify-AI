"""Natural Language Processing utilities."""

from typing import List, Dict, Tuple
from transformers import pipeline
import torch
from functools import lru_cache

class NLP:
    """Provides advanced NLP functionality including sentiment analysis, NER, and text processing."""
    
    def __init__(self):
        """Initialize NLP components with optimizations."""
        # Use GPU if available
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Initialize models with optimizations
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize models with optimizations."""
        # Shared config for all pipelines
        shared_config = {
            "device": self.device,
            "model_kwargs": {"torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32}
        }
        
        # Initialize pipelines with optimizations
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",  # Smaller, faster model
            **shared_config
        )
        
        self.ner_pipeline = pipeline(
            "ner",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
            aggregation_strategy="simple",  # Faster aggregation
            **shared_config
        )
        
        self.zero_shot = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            **shared_config
        )
        
        # Pre-warm models
        self._warm_up_models()
        
    def _warm_up_models(self):
        """Warm up models with dummy inputs to ensure faster first inference."""
        dummy_text = "Hello world"
        self.sentiment_analyzer(dummy_text)
        self.ner_pipeline(dummy_text)
        self.zero_shot(dummy_text, ["test"])
    
    @lru_cache(maxsize=1000)
    def analyze_sentiment(self, text: str) -> float:
        """Analyze the sentiment of given text, returning a score."""
        result = self.sentiment_analyzer(text)[0]
        score = result['score']
        return score if result['label'] == 'POSITIVE' else -score
    
    @lru_cache(maxsize=1000)
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text with caching."""
        entities = self.ner_pipeline(text)
        
        # Group entities by type
        grouped_entities = {}
        for entity in entities:
            entity_type = entity['entity_group']
            entity_text = entity['word']
            if entity_type not in grouped_entities:
                grouped_entities[entity_type] = []
            if entity_text not in grouped_entities[entity_type]:
                grouped_entities[entity_type].append(entity_text)
                
        return grouped_entities
    
    @lru_cache(maxsize=1000)
    def extract_topics(self, text: str) -> List[Tuple[str, float]]:
        """Extract potential topics from text using zero-shot classification with caching."""
        # Define focused set of candidate topics
        candidate_labels = [
            "technology", "business", "personal",
            "general inquiry", "technical support",
            "feedback"
        ]
        
        # Use zero-shot classification with batching
        result = self.zero_shot(
            text, 
            candidate_labels,
            multi_label=True,
            batch_size=8  # Batch processing for efficiency
        )
        
        # Filter and sort results
        threshold = 0.3
        topics = [(label, score) for label, score in 
                 zip(result['labels'], result['scores']) 
                 if score > threshold]
        
        return sorted(topics, key=lambda x: x[1], reverse=True)
    
    def analyze_text(self, text: str) -> Dict:
        """Perform comprehensive text analysis with parallel processing."""
        # Create tasks for concurrent execution
        sentiment = self.analyze_sentiment(text)
        entities = self.extract_entities(text)
        topics = self.extract_topics(text)
        
        return {
            'sentiment': sentiment,
            'entities': entities,
            'topics': topics
        }
