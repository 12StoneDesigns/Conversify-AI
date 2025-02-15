# Conversify-AI

## Description

Conversify-AI is a conversational AI application designed to facilitate engaging and intelligent interactions. It leverages state-of-the-art transformer models and advanced NLP capabilities to provide sophisticated natural language understanding and processing.

### Key Features

- **Advanced Natural Language Processing**:
  - Transformer-based language understanding using Hugging Face models
  - Zero-shot topic classification
  - Named Entity Recognition (NER)
  - Sentiment analysis
  - Comprehensive text analysis

- **Intent Classification**:
  - Semantic similarity using sentence embeddings
  - Multi-intent detection
  - Confidence scoring
  - Entity and topic extraction

- **Language Understanding**:
  - Context-aware responses
  - Entity recognition and tracking
  - Topic detection with confidence scoring
  - Sentiment-aware interactions

## Installation

To set up the project, follow these steps:

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:

   ```bash
   cd Conversify-AI
   ```

3. Create and activate the virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Technical Details

Conversify-AI uses several powerful libraries and models:

- **PyTorch**: Deep learning framework for neural network operations
- **Transformers**: Hugging Face's transformer models for NLP tasks
  - Sentence embeddings using MiniLM
  - BERT-based Named Entity Recognition
  - Zero-shot classification for topic detection
- **scikit-learn**: For similarity calculations and machine learning utilities
- **NLTK**: For additional text processing capabilities

## Usage

To run the application, use the following command:

```bash
python main.py
```

### Example Capabilities

The system can:
- Detect multiple intents in user messages
- Extract named entities (people, organizations, locations)
- Identify topics with confidence scores
- Analyze sentiment in real-time
- Generate context-aware responses

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.

## Author

- **Name**: T. Landon Love
- **Company**: 12Stone Designs
- **Email**: [12stonedesigns@gmail.com](mailto:12stonedesigns@gmail.com)
