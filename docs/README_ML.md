# Hermes AI & Machine Learning Capabilities

This document covers the advanced AI and machine learning features in Hermes, including transformer-based classification and neural summarization capabilities.

## Overview

Hermes AI capabilities provide significant improvements over traditional rule-based systems:

- ML-based classification using transformer models (BERT, DistilBERT) or lightweight sentence embeddings
- NLP summarization with both extractive and abstractive approaches using BART, T5, and sentence transformers
- Advanced analytics including sentiment analysis, urgency detection, entity extraction, and topic modeling
- Fallback system that uses rule-based processing if ML models are unavailable

## Features

### ML-Based Intent Classification

Two approaches are available:

**Transformer-Based Classifier** (`classify_ml.py`):
- Uses DistilBERT for high-accuracy classification
- Supports fine-tuning on domain-specific data
- Provides confidence scores for predictions
- Handles 8 intent categories: bug_report, feature_request, how_to_question, troubleshooting, configuration, discussion, announcement, general

**Lightweight Classifier**:
- Uses sentence embeddings (MiniLM) with Random Forest
- Faster inference and lower memory usage
- Suitable for real-time processing
- Easy to retrain with new data

### NLP Summarization

**Abstractive Summarization** (`summarize_ml.py`):
- Uses BART-large-CNN for generating new summary text
- Produces human-like summaries
- Configurable summary length
- Handles various text lengths

**Extractive Summarization**:
- Selects key sentences from original text
- Uses sentence embeddings for ranking
- Considers position, length, keywords, and centrality
- Faster than abstractive approaches

**Hybrid Approach**:
- Combines both methods for optimal results
- Extractive selection followed by abstractive refinement
- Balances quality and performance

### Advanced Analytics

**Sentiment Analysis**:
- Detects positive, negative, or neutral sentiment
- Useful for understanding team morale and issue resolution

**Urgency Detection**:
- Classifies urgency levels: urgent, high, medium
- Helps prioritize support requests

**Entity Extraction**:
- Identifies technical terms, error codes, and technologies
- Useful for categorizing and indexing

**Topic Modeling**:
- Detects main topics: authentication, deployment, performance, etc.
- Enables better organization and routing

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Download NLTK Data (if needed)

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### Install Additional Models (Optional)

For better performance, you can pre-download specific models:

```bash
# Download specific transformers models
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('distilbert-base-uncased'); AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased')"

# Download summarization models
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('facebook/bart-large-cnn'); AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-large-cnn')"
```

## Usage

### Basic ML Processing

```bash
# Use ML-based processing with lightweight models
python3 run_pipeline_ml.py --use-ml --lightweight

# Use full transformer models
python3 run_pipeline_ml.py --use-ml

# Compare rule-based vs ML-based processing
python3 run_pipeline_ml.py --compare
```

### Training Your Own Models

```bash
# Train models with synthetic data (for demonstration)
python3 train_models.py --synthetic

# Train with your own data
python3 train_models.py --data-file your_data.json

# Train only classification models
python3 train_models.py --classify-only --synthetic

# Demonstrate trained models
python3 train_models.py --demo
```

### Command Line Options

`run_pipeline_ml.py` Options:
- `--use-ml`: Enable ML-based processing
- `--lightweight`: Use lightweight models for faster processing
- `--compare`: Compare rule-based vs ML approaches
- `--max-threads N`: Process only N threads
- `--data-file FILE`: Specify input data file

`train_models.py` Options:
- `--synthetic`: Generate synthetic training data
- `--data-file FILE`: Use specific training data file
- `--classify-only`: Train only classification models
- `--demo`: Demonstrate trained models

## Model Architecture

### Classification Models

```
Input Text → Tokenization → Transformer/Embedding → Classification Head → Intent + Confidence
```

Transformer Approach:
- Input: Thread text (max 512 tokens)
- Model: DistilBERT (66M parameters)
- Output: 8-class classification with confidence scores

Lightweight Approach:
- Input: Thread text (any length)
- Model: MiniLM sentence embeddings + Random Forest
- Output: Classification with probability scores

### Summarization Models

```
Input Text → Preprocessing → Model → Summary
```

Abstractive (BART):
- Input: Processed thread text
- Model: BART-large-CNN (400M parameters)
- Output: Generated summary text

Extractive:
- Input: Original thread sentences
- Model: Sentence embeddings + ranking algorithm
- Output: Selected key sentences

## Configuration

### Model Selection

Configure which models to use by modifying the initialization:

```python
# Use different classification models
classify_ml.initialize_ml_models(use_lightweight=True)

# Use different summarization models
summarize_ml.initialize_ml_summarizer(
    abstractive_model="facebook/bart-large-cnn",
    extractive_model="all-MiniLM-L6-v2"
)
```

### Performance Tuning

For speed optimization:
- Use lightweight classification models
- Use extractive summarization only
- Reduce max_length for summarization

For quality optimization:
- Use full transformer models
- Use hybrid summarization
- Increase model size (e.g., BART-large)

## Training Data

### Data Format

Training data should follow this structure:

```json
[
  {
    "thread_ts": "timestamp",
    "messages": [
      {
        "ts": "timestamp",
        "user": "username",
        "text": "message content"
      }
    ],
    "true_intent": "bug_report"  // Optional ground truth
  }
]
```

### Data Preparation

1. Collect real data by exporting actual Slack threads from your channels
2. Annotate by adding ground truth labels for intent classification
3. Clean by removing sensitive information and normalizing text
4. Split into training/validation/test sets

### Synthetic Data Generation

For demonstration or initial training:

```python
from train_models import create_synthetic_training_data

# Generate 1000 synthetic examples
synthetic_data = create_synthetic_training_data(1000)
```

## Performance Metrics

### Classification Metrics

- Accuracy: Overall classification accuracy
- Precision/Recall: Per-class performance
- F1-Score: Balanced precision/recall measure
- Confidence: Model certainty in predictions

### Summarization Metrics

- ROUGE: Overlap-based evaluation (when reference summaries available)
- BERT-Score: Semantic similarity evaluation
- Length: Summary length statistics
- Processing Time: Speed metrics

## Comparison: Rule-Based vs ML-Based

| Aspect | Rule-Based | ML-Based |
|--------|------------|----------|
| Accuracy | ~70-80% | ~85-95% |
| Speed | Very Fast | Moderate |
| Memory | Low | High |
| Customization | Manual rules | Data-driven |
| Maintenance | High | Low |
| Interpretability | High | Low |

## Troubleshooting

### Common Issues

1. CUDA Out of Memory:
   ```bash
   # Use CPU-only processing
   export CUDA_VISIBLE_DEVICES=""
   
   # Or use lightweight models
   python3 run_pipeline_ml.py --use-ml --lightweight
   ```

2. Model Download Failures:
   ```bash
   # Pre-download models
   python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('distilbert-base-uncased')"
   ```

3. Import Errors:
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   ```

### Performance Optimization

1. Batch Processing: Process multiple threads at once
2. Model Caching: Pre-load models to avoid repeated loading
3. Quantization: Use quantized models for faster inference
4. GPU Acceleration: Use CUDA if available

## Future Enhancements

### Planned Features

1. Real-time processing with WebSocket integration for live analysis
2. Multi-language support for non-English threads
3. Custom fine-tuning on domain-specific data
4. REST API for external applications
5. Advanced analytics with more sophisticated NLP analysis

### Model Improvements

1. Domain adaptation by fine-tuning on software engineering data
2. Few-shot learning for better performance with limited data
3. Ensemble methods combining multiple models for better accuracy
4. Explainable AI for understanding model decisions

## Contributing

### Adding New Models

1. Classification: Extend `classify_ml.py` with new classifier classes
2. Summarization: Add new summarization approaches to `summarize_ml.py`
3. Analytics: Extend insight extraction in `extract_key_insights()`

### Training New Models

1. Collect domain-specific training data
2. Add ground truth labels
3. Use `train_models.py` as a starting point
4. Test on held-out data
5. Update model loading in the pipeline

## License

This project maintains the same license as the Hermes Communication Intelligence System.

## Support

For issues related to Hermes AI features:
1. Check the troubleshooting section in HERMES_SETUP_GUIDE.md
2. Verify dependencies are installed correctly
3. Test with synthetic data first
4. Check GPU/CPU compatibility
5. Use the web dashboard for easier troubleshooting 