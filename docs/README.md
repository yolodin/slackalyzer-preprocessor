# Hermes Communication Intelligence System

Hermes is an AI-powered communication intelligence platform that processes Slack conversations to extract actionable insights. Named after the Greek god of communication, this system analyzes support interactions, identifies patterns, and discovers automation opportunities in engineering environments.

## Overview

Hermes takes raw Slack export data and transforms it into structured, analyzable intelligence. It performs thread formatting, AI-powered summarization, intent classification, and timing analysis to deliver actionable insights for team optimization and automation discovery.

## Features

- Thread message formatting and preprocessing
- Automatic summarization of conversation threads
- Rule-based intent classification (bug reports, feature requests, questions, etc.)
- Response time calculation and duration analysis
- Robust error handling for production reliability
- Detailed processing statistics and insights

## Project Structure

```
Hermes/
├── start_hermes.py          # 🚀 Main startup script
├── src/slackops/            # Core AI processing engine
│   ├── preprocess.py        # Message formatting and metadata extraction
│   ├── summarize.py         # Thread summarization logic
│   ├── classify.py          # Intent detection and classification
│   ├── summarize_ml.py      # AI-powered summarization
│   └── classify_ml.py       # ML-based intent classification
├── web-dashboard/           # Modern React frontend
├── data/                    # Slack export files
├── scripts/                 # Processing pipelines
└── docs/                    # Comprehensive documentation
```

## Installation

This project requires Python 3.7 or higher. Clone the repository and install dependencies:

```bash
git clone <your-repository-url>
cd Hermes

# Quick start - runs everything automatically
python3 start_hermes.py
```

## Usage

### Quick Start

Launch the complete Hermes system:

```bash
# Start web dashboard and API server
python3 start_hermes.py

# Or use command-line processing
python3 scripts/run_pipeline_ml.py --use-ml
```

### Input Format

The pipeline expects JSON data in Slack export format:

```json
[
  {
    "thread_ts": "1671024600.123456",
    "messages": [
      {
        "ts": "1671024600.123456",
        "user": "user1",
        "text": "Message content here"
      }
    ]
  }
]
```

### Output

For each processed thread, the pipeline outputs:

- Thread ID: Unique identifier from Slack
- Summary: Automated description of thread content and type
- Intent: Classified category (bug_report, feature_request, how_to_question, etc.)
- Duration: Time span from first to last message
- Metadata: Message count, user count, confidence scores

## Components

### Preprocessing Module (`preprocess.py`)

Handles raw message formatting and metadata extraction:
- Converts timestamps to human-readable format
- Formats user messages into readable thread representations
- Extracts timing information and participant counts

### Summarization Module (`summarize.py`)

Generates concise summaries of thread content:
- Identifies thread type (support issue, discussion, etc.)
- Extracts key participants and message flow
- Creates preview text from initial messages

### Classification Module (`classify.py`)

Performs rule-based intent detection:
- Bug reports and error discussions
- Feature requests and enhancement proposals
- How-to questions and troubleshooting
- Announcements and general discussions
- Confidence scoring for classification results

## Configuration

The pipeline can be configured by modifying the data file path in `run_pipeline.py`:

```python
data_file = "data/your_slack_export.json"
```

## Error Handling

The pipeline includes comprehensive error handling:
- Individual thread failures don't stop processing
- Detailed error reporting with exception types
- Processing statistics and success rates
- Graceful handling of malformed data

## Development

To extend the pipeline:

1. Add new intent categories: Modify the patterns in `classify.py`
2. Enhance summarization: Update logic in `summarize.py`
3. Custom preprocessing: Extend functions in `preprocess.py`
4. Output formats: Modify result structure in `run_pipeline.py`

## Sample Data

The included sample data contains 5 representative threads:
- Authentication error resolution
- Docker setup question
- Database connection troubleshooting
- Version release announcement
- Feature request discussion

## Performance

Processing time scales approximately linearly with thread count. Typical performance:
- 100 threads: ~2-3 seconds
- 1000 threads: ~20-30 seconds
- Memory usage: <50MB for typical datasets

## Advanced Features

✅ **Already Implemented:**
- Machine learning-based classification (DistilBERT, MiniLM)
- Advanced NLP summarization (BART, T5, sentence transformers)
- Modern web dashboard with real-time monitoring
- RESTful API for external integration
- Multi-format Slack data adapter

🚀 **Future Enhancements:**
- Real-time Slack integration
- Multi-language support
- Predictive analytics
- Integration with ticketing systems
