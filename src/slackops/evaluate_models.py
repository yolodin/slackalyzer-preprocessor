#!/usr/bin/env python3
"""
Evaluation script for AI models in Hermes Communication Intelligence System.
"""

import json
import time
import os
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Import our modules
from . import preprocess
from . import classify
from . import summarize
from . import classify_ml
from . import summarize_ml
from .train_models import create_synthetic_training_data


def evaluate_classification_models(test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate classification models on test data.
    
    Args:
        test_data: List of test thread data with ground truth labels
        
    Returns:
        Dictionary with evaluation results
    """
    print("=" * 60)
    print("EVALUATING CLASSIFICATION MODELS")
    print("=" * 60)
    
    # Prepare test data
    texts = []
    true_labels = []
    
    for thread in test_data:
        formatted_text = preprocess.format_thread_messages(thread)
        texts.append(formatted_text)
        
        # Get ground truth label
        if "true_intent" in thread:
            true_labels.append(thread["true_intent"])
        else:
            # Use rule-based as ground truth if no annotation available
            true_labels.append(classify.detect_intent(formatted_text))
    
    print(f"Evaluating on {len(texts)} test samples")
    
    results = {}
    
    # Test rule-based classification
    print("\nTesting Rule-based Classification...")
    rule_predictions = []
    rule_confidences = []
    rule_times = []
    
    for text in texts:
        start_time = time.time()
        prediction = classify.detect_intent(text)
        confidence = classify.get_confidence_score(text, prediction)
        end_time = time.time()
        
        rule_predictions.append(prediction)
        rule_confidences.append(confidence)
        rule_times.append(end_time - start_time)
    
    rule_accuracy = accuracy_score(true_labels, rule_predictions)
    results['rule_based'] = {
        'accuracy': rule_accuracy,
        'avg_confidence': np.mean(rule_confidences),
        'avg_time': np.mean(rule_times),
        'predictions': rule_predictions,
        'confidences': rule_confidences
    }
    
    print(f"Rule-based Accuracy: {rule_accuracy:.4f}")
    print(f"Average Confidence: {np.mean(rule_confidences):.4f}")
    print(f"Average Time: {np.mean(rule_times):.4f}s")
    
    # Test ML-based classification if available
    try:
        print("\nTesting ML-based Classification...")
        classify_ml.initialize_ml_models(use_lightweight=True)
        
        ml_predictions = []
        ml_confidences = []
        ml_times = []
        
        for text in texts:
            start_time = time.time()
            prediction = classify_ml.detect_intent_ml(text, use_lightweight=True)
            confidence = classify_ml.get_confidence_score_ml(text, prediction, use_lightweight=True)
            end_time = time.time()
            
            ml_predictions.append(prediction)
            ml_confidences.append(confidence)
            ml_times.append(end_time - start_time)
        
        ml_accuracy = accuracy_score(true_labels, ml_predictions)
        results['ml_based'] = {
            'accuracy': ml_accuracy,
            'avg_confidence': np.mean(ml_confidences),
            'avg_time': np.mean(ml_times),
            'predictions': ml_predictions,
            'confidences': ml_confidences
        }
        
        print(f"ML-based Accuracy: {ml_accuracy:.4f}")
        print(f"Average Confidence: {np.mean(ml_confidences):.4f}")
        print(f"Average Time: {np.mean(ml_times):.4f}s")
        
    except Exception as e:
        print(f"ML-based classification not available: {e}")
        results['ml_based'] = None
    
    # Generate detailed classification report
    print("\nDetailed Classification Report (Rule-based):")
    print(classification_report(true_labels, rule_predictions))
    
    if results['ml_based']:
        print("\nDetailed Classification Report (ML-based):")
        print(classification_report(true_labels, ml_predictions))
    
    return results


def evaluate_summarization_models(test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate summarization models on test data.
    
    Args:
        test_data: List of test thread data
        
    Returns:
        Dictionary with evaluation results
    """
    print("=" * 60)
    print("EVALUATING SUMMARIZATION MODELS")
    print("=" * 60)
    
    # Prepare test data
    texts = []
    for thread in test_data:
        formatted_text = preprocess.format_thread_messages(thread)
        texts.append(formatted_text)
    
    print(f"Evaluating on {len(texts)} test samples")
    
    results = {}
    
    # Test rule-based summarization
    print("\nTesting Rule-based Summarization...")
    rule_summaries = []
    rule_times = []
    
    for text in texts:
        start_time = time.time()
        summary = summarize.generate_summary(text)
        end_time = time.time()
        
        rule_summaries.append(summary)
        rule_times.append(end_time - start_time)
    
    results['rule_based'] = {
        'summaries': rule_summaries,
        'avg_time': np.mean(rule_times),
        'avg_length': np.mean([len(s.split()) for s in rule_summaries])
    }
    
    print(f"Rule-based Average Time: {np.mean(rule_times):.4f}s")
    print(f"Rule-based Average Length: {np.mean([len(s.split()) for s in rule_summaries]):.1f} words")
    
    # Test ML-based summarization if available
    try:
        print("\nTesting ML-based Summarization...")
        summarize_ml.initialize_ml_summarizer()
        
        # Test extractive summarization
        extractive_summaries = []
        extractive_times = []
        
        for text in texts:
            start_time = time.time()
            summary = summarize_ml.generate_summary_ml(text, approach="extractive")
            end_time = time.time()
            
            extractive_summaries.append(summary)
            extractive_times.append(end_time - start_time)
        
        results['extractive'] = {
            'summaries': extractive_summaries,
            'avg_time': np.mean(extractive_times),
            'avg_length': np.mean([len(s.split()) for s in extractive_summaries])
        }
        
        print(f"Extractive Average Time: {np.mean(extractive_times):.4f}s")
        print(f"Extractive Average Length: {np.mean([len(s.split()) for s in extractive_summaries]):.1f} words")
        
        # Test abstractive summarization
        abstractive_summaries = []
        abstractive_times = []
        
        for text in texts:
            start_time = time.time()
            summary = summarize_ml.generate_summary_ml(text, approach="abstractive")
            end_time = time.time()
            
            abstractive_summaries.append(summary)
            abstractive_times.append(end_time - start_time)
        
        results['abstractive'] = {
            'summaries': abstractive_summaries,
            'avg_time': np.mean(abstractive_times),
            'avg_length': np.mean([len(s.split()) for s in abstractive_summaries])
        }
        
        print(f"Abstractive Average Time: {np.mean(abstractive_times):.4f}s")
        print(f"Abstractive Average Length: {np.mean([len(s.split()) for s in abstractive_summaries]):.1f} words")
        
    except Exception as e:
        print(f"ML-based summarization not available: {e}")
        results['extractive'] = None
        results['abstractive'] = None
    
    return results


def create_evaluation_plots(classification_results: Dict[str, Any], 
                           summarization_results: Dict[str, Any],
                           output_dir: str = "evaluation_plots"):
    """
    Create evaluation plots and save them.
    
    Args:
        classification_results: Results from classification evaluation
        summarization_results: Results from summarization evaluation
        output_dir: Directory to save plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Classification accuracy comparison
    if classification_results['ml_based']:
        plt.figure(figsize=(10, 6))
        
        methods = ['Rule-based', 'ML-based']
        accuracies = [
            classification_results['rule_based']['accuracy'],
            classification_results['ml_based']['accuracy']
        ]
        confidences = [
            classification_results['rule_based']['avg_confidence'],
            classification_results['ml_based']['avg_confidence']
        ]
        times = [
            classification_results['rule_based']['avg_time'] * 1000,  # Convert to ms
            classification_results['ml_based']['avg_time'] * 1000
        ]
        
        # Accuracy comparison
        plt.subplot(1, 3, 1)
        plt.bar(methods, accuracies, color=['skyblue', 'lightgreen'])
        plt.title('Classification Accuracy')
        plt.ylabel('Accuracy')
        plt.ylim(0, 1)
        
        # Add value labels on bars
        for i, v in enumerate(accuracies):
            plt.text(i, v + 0.01, f'{v:.3f}', ha='center')
        
        # Confidence comparison
        plt.subplot(1, 3, 2)
        plt.bar(methods, confidences, color=['skyblue', 'lightgreen'])
        plt.title('Average Confidence')
        plt.ylabel('Confidence')
        plt.ylim(0, 1)
        
        for i, v in enumerate(confidences):
            plt.text(i, v + 0.01, f'{v:.3f}', ha='center')
        
        # Time comparison
        plt.subplot(1, 3, 3)
        plt.bar(methods, times, color=['skyblue', 'lightgreen'])
        plt.title('Average Processing Time')
        plt.ylabel('Time (ms)')
        
        for i, v in enumerate(times):
            plt.text(i, v + 0.1, f'{v:.1f}ms', ha='center')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/classification_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # Summarization comparison
    if summarization_results.get('extractive') and summarization_results.get('abstractive'):
        plt.figure(figsize=(12, 6))
        
        methods = ['Rule-based', 'Extractive', 'Abstractive']
        times = [
            summarization_results['rule_based']['avg_time'] * 1000,
            summarization_results['extractive']['avg_time'] * 1000,
            summarization_results['abstractive']['avg_time'] * 1000
        ]
        lengths = [
            summarization_results['rule_based']['avg_length'],
            summarization_results['extractive']['avg_length'],
            summarization_results['abstractive']['avg_length']
        ]
        
        # Time comparison
        plt.subplot(1, 2, 1)
        plt.bar(methods, times, color=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('Summarization Processing Time')
        plt.ylabel('Time (ms)')
        plt.xticks(rotation=45)
        
        for i, v in enumerate(times):
            plt.text(i, v + max(times) * 0.01, f'{v:.1f}ms', ha='center')
        
        # Length comparison
        plt.subplot(1, 2, 2)
        plt.bar(methods, lengths, color=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('Average Summary Length')
        plt.ylabel('Words')
        plt.xticks(rotation=45)
        
        for i, v in enumerate(lengths):
            plt.text(i, v + max(lengths) * 0.01, f'{v:.1f}', ha='center')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/summarization_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Plots saved to {output_dir}/")


def benchmark_performance(num_samples: int = 100):
    """
    Benchmark performance on synthetic data.
    
    Args:
        num_samples: Number of samples to generate for benchmarking
    """
    print("=" * 60)
    print("PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # Generate synthetic test data
    print(f"Generating {num_samples} synthetic test samples...")
    test_data = create_synthetic_training_data(num_samples)
    
    # Evaluate classification models
    classification_results = evaluate_classification_models(test_data)
    
    # Evaluate summarization models
    summarization_results = evaluate_summarization_models(test_data)
    
    # Create evaluation plots
    try:
        create_evaluation_plots(classification_results, summarization_results)
    except Exception as e:
        print(f"Error creating plots: {e}")
    
    # Save results
    results = {
        'classification': classification_results,
        'summarization': summarization_results,
        'test_samples': num_samples
    }
    
    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to evaluation_results.json")
    
    return results


def compare_sample_outputs(num_samples: int = 3):
    """
    Compare outputs from different models on sample data.
    
    Args:
        num_samples: Number of samples to compare
    """
    print("=" * 60)
    print("SAMPLE OUTPUT COMPARISON")
    print("=" * 60)
    
    # Generate sample data
    sample_data = create_synthetic_training_data(num_samples)
    
    # Initialize ML models
    try:
        classify_ml.initialize_ml_models(use_lightweight=True)
        summarize_ml.initialize_ml_summarizer()
        ml_available = True
    except Exception as e:
        print(f"ML models not available: {e}")
        ml_available = False
    
    for i, thread in enumerate(sample_data, 1):
        print(f"\nSample {i}:")
        print("-" * 40)
        
        # Format thread
        formatted_text = preprocess.format_thread_messages(thread)
        print(f"Original Text: {formatted_text[:200]}...")
        
        # Ground truth
        if "true_intent" in thread:
            print(f"Ground Truth Intent: {thread['true_intent']}")
        
        # Classification comparison
        print("\nClassification Results:")
        
        # Rule-based
        rule_intent = classify.detect_intent(formatted_text)
        rule_confidence = classify.get_confidence_score(formatted_text, rule_intent)
        print(f"  Rule-based: {rule_intent} (confidence: {rule_confidence:.3f})")
        
        # ML-based
        if ml_available:
            try:
                ml_intent = classify_ml.detect_intent_ml(formatted_text, use_lightweight=True)
                ml_confidence = classify_ml.get_confidence_score_ml(formatted_text, ml_intent, use_lightweight=True)
                print(f"  ML-based: {ml_intent} (confidence: {ml_confidence:.3f})")
            except Exception as e:
                print(f"  ML-based: Error - {e}")
        
        # Summarization comparison
        print("\nSummarization Results:")
        
        # Rule-based
        rule_summary = summarize.generate_summary(formatted_text)
        print(f"  Rule-based: {rule_summary}")
        
        # ML-based
        if ml_available:
            try:
                extractive_summary = summarize_ml.generate_summary_ml(formatted_text, "extractive")
                print(f"  Extractive: {extractive_summary}")
                
                abstractive_summary = summarize_ml.generate_summary_ml(formatted_text, "abstractive")
                print(f"  Abstractive: {abstractive_summary}")
            except Exception as e:
                print(f"  ML-based: Error - {e}")
        
        print("-" * 40)


def main():
    """Main evaluation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate AI models for Hermes Communication Intelligence System")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark")
    parser.add_argument("--compare", action="store_true", help="Compare sample outputs")
    parser.add_argument("--num-samples", type=int, default=100, help="Number of samples for evaluation")
    parser.add_argument("--data-file", type=str, help="Use specific test data file")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_sample_outputs(num_samples=min(args.num_samples, 5))
    elif args.benchmark:
        benchmark_performance(num_samples=args.num_samples)
    else:
        print("Please specify --benchmark or --compare")
        print("Use --help for more options")


if __name__ == "__main__":
    main() 