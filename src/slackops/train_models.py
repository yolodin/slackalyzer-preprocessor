#!/usr/bin/env python3
"""
Training script for AI models in Hermes Communication Intelligence System.
"""

import json
import os
import argparse
from typing import Dict, Any, List, Tuple
from datetime import datetime
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import random

# Import our modules
from . import preprocess
from . import classify_ml
from . import summarize_ml


def create_synthetic_training_data(num_samples: int = 1000) -> List[Dict[str, Any]]:
    """
    Create synthetic training data for demonstration.
    In practice, you'd use real, human-annotated data.
    """
    
    # Sample thread templates
    templates = {
        "bug_report": [
            "I'm getting an error when trying to {action}. The error message is: {error}",
            "Something is broken with {component}. It's showing {error}",
            "There's a bug in {component} that causes {error}",
            "The {component} is not working properly. I see {error}"
        ],
        "feature_request": [
            "Would it be possible to add {feature} to {component}?",
            "I'd like to request a new feature: {feature}",
            "Can we enhance {component} with {feature}?",
            "It would be great if we could {feature}"
        ],
        "how_to_question": [
            "How do I {action} in {component}?",
            "What are the steps to {action}?",
            "Can someone help me understand how to {action}?",
            "I need help with {action}"
        ],
        "troubleshooting": [
            "I'm having trouble with {component}. It's not {expected_behavior}",
            "Help! My {component} is not working correctly",
            "Something is wrong with {component}",
            "I can't get {component} to work properly"
        ],
        "configuration": [
            "How do I configure {component} for {environment}?",
            "What are the correct settings for {component}?",
            "I need help setting up {component}",
            "Configuration issue with {component}"
        ],
        "discussion": [
            "What do you think about {topic}?",
            "I'd like to discuss {topic}",
            "Let's talk about {topic}",
            "Thoughts on {topic}?"
        ],
        "announcement": [
            "FYI: We're releasing {component} version {version}",
            "Heads up: {component} maintenance scheduled",
            "Announcement: {topic}",
            "Update: {topic}"
        ]
    }
    
    # Sample data for placeholders
    actions = ["deploy", "authenticate", "connect", "install", "configure", "setup"]
    components = ["API", "database", "authentication service", "web server", "Docker", "Kubernetes"]
    errors = ["500 Internal Server Error", "Connection timeout", "Authentication failed", "Permission denied"]
    features = ["bulk export", "real-time notifications", "advanced filtering", "dashboard widgets"]
    environments = ["production", "staging", "development", "testing"]
    topics = ["performance optimization", "security updates", "new architecture", "team processes"]
    versions = ["2.1.0", "1.5.3", "3.0.0", "1.2.1"]
    
    synthetic_data = []
    
    for i in range(num_samples):
        # Randomly select intent and template
        intent = random.choice(list(templates.keys()))
        template = random.choice(templates[intent])
        
        # Fill in placeholders
        message = template.format(
            action=random.choice(actions),
            component=random.choice(components),
            error=random.choice(errors),
            feature=random.choice(features),
            environment=random.choice(environments),
            topic=random.choice(topics),
            version=random.choice(versions),
            expected_behavior="working as expected"
        )
        
        # Create thread structure
        thread = {
            "thread_ts": f"167{random.randint(1000000, 9999999)}.{random.randint(100000, 999999)}",
            "messages": [
                {
                    "ts": f"167{random.randint(1000000, 9999999)}.{random.randint(100000, 999999)}",
                    "user": f"user{random.randint(1, 10)}",
                    "text": message
                }
            ],
            "true_intent": intent  # Ground truth label
        }
        
        # Add follow-up messages for some threads
        if random.random() < 0.3:  # 30% chance of follow-up
            follow_up = {
                "ts": f"167{random.randint(1000000, 9999999)}.{random.randint(100000, 999999)}",
                "user": f"user{random.randint(1, 10)}",
                "text": random.choice([
                    "Thanks for the help!",
                    "That worked perfectly.",
                    "I'm still having issues.",
                    "Can you provide more details?",
                    "I'll try that approach."
                ])
            }
            thread["messages"].append(follow_up)
        
        synthetic_data.append(thread)
    
    return synthetic_data


def prepare_classification_data(threads: List[Dict[str, Any]]) -> tuple:
    """
    Prepare data for classification model training.
    
    Args:
        threads: List of thread dictionaries
        
    Returns:
        Tuple of (texts, labels)
    """
    texts = []
    labels = []
    
    for thread in threads:
        # Format thread for ML processing
        formatted_text = preprocess.format_thread_messages(thread)
        
        # Use ground truth label if available, otherwise use rule-based
        if "true_intent" in thread:
            label = thread["true_intent"]
        else:
            label = classify_ml.classify.detect_intent(formatted_text)
        
        texts.append(formatted_text)
        labels.append(label)
    
    return texts, labels


def train_classification_models(data_file: str = None, use_synthetic: bool = False):
    """
    Train classification models.
    
    Args:
        data_file: Path to training data file
        use_synthetic: Whether to generate synthetic data
    """
    print("=" * 60)
    print("TRAINING CLASSIFICATION MODELS")
    print("=" * 60)
    
    # Load or generate training data
    if use_synthetic:
        print("Generating synthetic training data...")
        threads = create_synthetic_training_data(num_samples=1000)
    else:
        if not data_file:
            print("No data file provided. Using sample data...")
            data_file = "data/slack_export_sample.json"
        
        print(f"Loading training data from {data_file}...")
        with open(data_file, 'r') as f:
            threads = json.load(f)
    
    # Prepare data
    texts, labels = prepare_classification_data(threads)
    print(f"Prepared {len(texts)} training examples")
    
    # Print label distribution
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1
    
    print("\nLabel distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count}")
    
    # Train transformer-based classifier
    print("\n" + "-" * 40)
    print("Training Transformer-based Classifier")
    print("-" * 40)
    
    try:
        ml_classifier = classify_ml.MLIntentClassifier()
        ml_classifier.train_model(texts, labels)
        print("✓ Transformer-based classifier trained successfully")
    except Exception as e:
        print(f"✗ Error training transformer classifier: {e}")
    
    # Train lightweight classifier
    print("\n" + "-" * 40)
    print("Training Lightweight Classifier")
    print("-" * 40)
    
    try:
        lightweight_classifier = classify_ml.SentenceEmbeddingClassifier()
        lightweight_classifier.train_lightweight_model(texts, labels)
        print("✓ Lightweight classifier trained successfully")
    except Exception as e:
        print(f"✗ Error training lightweight classifier: {e}")


def prepare_summarization_data(threads: List[Dict[str, Any]]) -> tuple:
    """
    Prepare data for summarization model training.
    
    Args:
        threads: List of thread dictionaries
        
    Returns:
        Tuple of (full_texts, summaries)
    """
    full_texts = []
    summaries = []
    
    for thread in threads:
        # Format full thread
        formatted_text = preprocess.format_thread_messages(thread)
        
        # Generate reference summary (in practice, you'd have human-written summaries)
        reference_summary = summarize_ml.summarize.generate_summary(formatted_text)
        
        full_texts.append(formatted_text)
        summaries.append(reference_summary)
    
    return full_texts, summaries


def demonstrate_models():
    """
    Demonstrate the trained models on sample data.
    """
    print("=" * 60)
    print("DEMONSTRATING TRAINED MODELS")
    print("=" * 60)
    
    # Load sample data
    try:
        with open("data/slack_export_sample.json", 'r') as f:
            sample_threads = json.load(f)
    except FileNotFoundError:
        print("Sample data not found. Creating synthetic examples...")
        sample_threads = create_synthetic_training_data(num_samples=3)
    
    # Initialize models
    print("Initializing models...")
    try:
        classify_ml.initialize_ml_models(use_lightweight=True)
        summarize_ml.initialize_ml_summarizer()
        print("✓ Models initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing models: {e}")
        return
    
    # Process sample threads
    print("\nProcessing sample threads...")
    print("-" * 40)
    
    for i, thread in enumerate(sample_threads[:3], 1):
        print(f"\nThread {i}:")
        
        # Format thread
        formatted_text = preprocess.format_thread_messages(thread)
        print(f"Original: {formatted_text[:100]}...")
        
        # Classification
        try:
            intent = classify_ml.detect_intent_ml(formatted_text, use_lightweight=True)
            confidence = classify_ml.get_confidence_score_ml(formatted_text, intent, use_lightweight=True)
            print(f"Classification: {intent} (confidence: {confidence:.3f})")
        except Exception as e:
            print(f"Classification error: {e}")
        
        # Summarization
        try:
            extractive_summary = summarize_ml.generate_summary_ml(formatted_text, "extractive")
            print(f"Extractive Summary: {extractive_summary}")
            
            # Try abstractive if available
            abstractive_summary = summarize_ml.generate_summary_ml(formatted_text, "abstractive")
            print(f"Abstractive Summary: {abstractive_summary}")
        except Exception as e:
            print(f"Summarization error: {e}")
        
        print("-" * 40)


def main():
    """Main function for training script."""
    parser = argparse.ArgumentParser(description="Train AI models for Hermes Communication Intelligence System")
    parser.add_argument("--data-file", type=str, help="Path to training data file")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic training data")
    parser.add_argument("--classify-only", action="store_true", help="Train only classification models")
    parser.add_argument("--summarize-only", action="store_true", help="Train only summarization models")
    parser.add_argument("--demo", action="store_true", help="Demonstrate trained models")
    
    args = parser.parse_args()
    
    if args.demo:
        demonstrate_models()
        return
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    if not args.summarize_only:
        train_classification_models(data_file=args.data_file, use_synthetic=args.synthetic)
    
    if not args.classify_only:
        print("\n" + "=" * 60)
        print("SUMMARIZATION MODEL TRAINING")
        print("=" * 60)
        print("Note: Abstractive summarization models are pre-trained.")
        print("Extractive summarization uses sentence transformers.")
        print("For custom summarization, fine-tune on your domain data.")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print("Models saved in the 'models/' directory")
    print("Run with --demo to test the trained models")


if __name__ == "__main__":
    main() 