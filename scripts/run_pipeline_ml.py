#!/usr/bin/env python3
"""
Enhanced pipeline script for processing Slack thread exports with ML capabilities.
"""

import json
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import our modules
from slackops import preprocess
from slackops import summarize
from slackops import classify

# Import ML modules with error handling
try:
    from slackops import classify_ml
    from slackops import summarize_ml
    ML_AVAILABLE = True
except ImportError as e:
    print(f"ML modules not available: {e}")
    print("Falling back to rule-based processing only")
    ML_AVAILABLE = False


def load_slack_export(file_path: str) -> List[Dict[str, Any]]:
    """Load Slack export data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Successfully loaded {len(data)} threads from {file_path}")
        return data
    
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        raise


def process_single_thread(thread_data: Dict[str, Any], use_ml: bool = False, 
                         use_lightweight: bool = False) -> Dict[str, Any]:
    """
    Process a single Slack thread through the pipeline.
    
    Args:
        thread_data: Dictionary containing thread information
        use_ml: Whether to use ML-based processing
        use_lightweight: Whether to use lightweight ML models
        
    Returns:
        Dictionary with processing results
    """
    thread_id = thread_data.get('thread_ts', 'unknown')
    
    # Step 1: Format thread messages
    formatted_text = preprocess.format_thread_messages(thread_data)
    
    # Step 2: Extract metadata
    metadata = preprocess.extract_thread_metadata(thread_data)
    
    # Step 3: Generate summary
    if use_ml and ML_AVAILABLE:
        # Use ML-based summarization
        summary = summarize_ml.generate_summary_ml(formatted_text, approach="hybrid")
        
        # Get additional insights
        try:
            insights = summarize_ml.extract_key_insights(formatted_text)
            additional_info = {
                'entities': insights.get('entities', []),
                'topics': insights.get('topics', []),
                'sentiment': insights.get('sentiment', 'neutral'),
                'urgency': insights.get('urgency', 'medium')
            }
        except Exception as e:
            print(f"Error extracting insights for thread {thread_id}: {e}")
            additional_info = {}
    else:
        # Use rule-based summarization
        summary = summarize.generate_summary(formatted_text)
        additional_info = {}
    
    # Step 4: Detect intent
    if use_ml and ML_AVAILABLE:
        # Use ML-based classification
        intent = classify_ml.detect_intent_ml(formatted_text, metadata, use_lightweight)
        confidence = classify_ml.get_confidence_score_ml(formatted_text, intent, use_lightweight)
    else:
        # Use rule-based classification
        intent = classify.detect_intent(formatted_text, metadata)
        confidence = classify.get_confidence_score(formatted_text, intent)
    
    # Step 5: Calculate response duration
    duration = metadata.get('duration_seconds', 0)
    
    # Format duration in a human-readable way
    if duration > 0:
        if duration < 60:
            duration_str = f"{duration:.1f}s"
        elif duration < 3600:
            duration_str = f"{duration/60:.1f}m"
        else:
            duration_str = f"{duration/3600:.1f}h"
    else:
        duration_str = "0s"
    
    # Build result dictionary
    result = {
        'thread_id': thread_id,
        'summary': summary,
        'intent': intent,
        'confidence': confidence,
        'duration': duration_str,
        'duration_seconds': duration,
        'message_count': metadata.get('message_count', 0),
        'user_count': len(metadata.get('users', [])),
        'processing_method': 'ML' if use_ml and ML_AVAILABLE else 'Rule-based'
    }
    
    # Add ML-specific insights if available
    if additional_info:
        result.update(additional_info)
    
    return result


def initialize_ml_models(use_lightweight: bool = False):
    """
    Initialize ML models if available.
    
    Args:
        use_lightweight: Whether to use lightweight models
        
    Returns:
        Boolean indicating success
    """
    if not ML_AVAILABLE:
        return False
    
    try:
        print("Initializing ML models...")
        
        # Initialize classification models
        classify_ml.initialize_ml_models(use_lightweight=use_lightweight)
        
        # Initialize summarization models
        summarize_ml.initialize_ml_summarizer()
        
        print("✓ ML models initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error initializing ML models: {e}")
        print("Falling back to rule-based processing")
        return False


def compare_processing_methods(threads: List[Dict[str, Any]], max_threads: int = 5):
    """
    Compare rule-based and ML-based processing on sample threads.
    
    Args:
        threads: List of thread data
        max_threads: Maximum number of threads to compare
    """
    print("=" * 80)
    print("COMPARING PROCESSING METHODS")
    print("=" * 80)
    
    sample_threads = threads[:max_threads]
    
    for i, thread in enumerate(sample_threads, 1):
        thread_id = thread.get('thread_ts', f'thread_{i}')
        print(f"\nThread {i} (ID: {thread_id})")
        print("-" * 60)
        
        # Process with rule-based approach
        try:
            rule_result = process_single_thread(thread, use_ml=False)
            print("RULE-BASED:")
            print(f"  Summary: {rule_result['summary']}")
            print(f"  Intent: {rule_result['intent']} (confidence: {rule_result['confidence']:.3f})")
        except Exception as e:
            print(f"RULE-BASED ERROR: {e}")
        
        # Process with ML approach if available
        if ML_AVAILABLE:
            try:
                ml_result = process_single_thread(thread, use_ml=True, use_lightweight=True)
                print("ML-BASED:")
                print(f"  Summary: {ml_result['summary']}")
                print(f"  Intent: {ml_result['intent']} (confidence: {ml_result['confidence']:.3f})")
                
                # Show additional insights if available
                if 'sentiment' in ml_result:
                    print(f"  Sentiment: {ml_result['sentiment']}")
                if 'urgency' in ml_result:
                    print(f"  Urgency: {ml_result['urgency']}")
                if 'topics' in ml_result and ml_result['topics']:
                    print(f"  Topics: {', '.join(ml_result['topics'])}")
                    
            except Exception as e:
                print(f"ML-BASED ERROR: {e}")
        
        print("-" * 60)


def main():
    """Main function that orchestrates the enhanced pipeline."""
    parser = argparse.ArgumentParser(description="Hermes Communication Intelligence System with AI capabilities")
    parser.add_argument("--data-file", type=str, default="data/slack_export_sample.json",
                       help="Path to Slack export JSON file")
    parser.add_argument("--use-ml", action="store_true", 
                       help="Use ML-based processing instead of rule-based")
    parser.add_argument("--lightweight", action="store_true",
                       help="Use lightweight ML models for faster processing")
    parser.add_argument("--compare", action="store_true",
                       help="Compare rule-based vs ML-based processing")
    parser.add_argument("--max-threads", type=int, default=None,
                       help="Maximum number of threads to process")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ENHANCED SLACK THREAD ANALYZER - ML-ENABLED PIPELINE")
    print("=" * 80)
    
    # Initialize ML models if requested
    ml_initialized = False
    if args.use_ml or args.compare:
        ml_initialized = initialize_ml_models(use_lightweight=args.lightweight)
        if not ml_initialized and args.use_ml:
            print("ML models not available. Using rule-based processing instead.")
    
    try:
        # Load the data
        threads = load_slack_export(args.data_file)
        
        if not threads:
            print("No threads found in the data file.")
            return
        
        # Limit threads if specified
        if args.max_threads:
            threads = threads[:args.max_threads]
        
        # Compare processing methods if requested
        if args.compare:
            compare_processing_methods(threads)
            return
        
        print(f"\nProcessing {len(threads)} threads...")
        print(f"Mode: {'ML-based' if args.use_ml and ml_initialized else 'Rule-based'}")
        if args.use_ml and ml_initialized:
            print(f"ML Model Type: {'Lightweight' if args.lightweight else 'Full Transformer'}")
        print("-" * 80)
        
        successful_processes = 0
        failed_processes = 0
        results = []
        
        # Process each thread
        for i, thread_data in enumerate(threads, 1):
            thread_id = thread_data.get('thread_ts', f'thread_{i}')
            
            try:
                print(f"\nProcessing Thread {i}/{len(threads)} (ID: {thread_id})")
                
                # Process the thread
                result = process_single_thread(
                    thread_data, 
                    use_ml=args.use_ml and ml_initialized,
                    use_lightweight=args.lightweight
                )
                results.append(result)
                
                # Print the result
                print("✓ Successfully processed:")
                print(f"  Summary: {result['summary']}")
                print(f"  Intent: {result['intent']} (confidence: {result['confidence']:.3f})")
                print(f"  Duration: {result['duration']}")
                print(f"  Messages: {result['message_count']}, Users: {result['user_count']}")
                print(f"  Method: {result['processing_method']}")
                
                # Show additional ML insights if available
                if 'sentiment' in result:
                    print(f"  Sentiment: {result['sentiment']}")
                if 'urgency' in result:
                    print(f"  Urgency: {result['urgency']}")
                if 'topics' in result and result['topics']:
                    print(f"  Topics: {', '.join(result['topics'])}")
                
                successful_processes += 1
                
            except Exception as e:
                print(f"✗ Failed to process thread {thread_id}: {str(e)}")
                print(f"  Error type: {type(e).__name__}")
                failed_processes += 1
                
                # Add a failed result entry
                results.append({
                    'thread_id': thread_id,
                    'summary': 'Processing failed',
                    'intent': 'error',
                    'duration': '0s',
                    'error': str(e)
                })
        
        # Print summary statistics
        print("\n" + "=" * 80)
        print("PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Total threads: {len(threads)}")
        print(f"Successfully processed: {successful_processes}")
        print(f"Failed: {failed_processes}")
        print(f"Success rate: {(successful_processes/len(threads)*100):.1f}%")
        print(f"Processing method: {'ML-based' if args.use_ml and ml_initialized else 'Rule-based'}")
        
        # Print aggregated insights
        if successful_processes > 0:
            print("\n" + "-" * 80)
            print("INSIGHTS")
            print("-" * 80)
            
            # Intent distribution
            intent_counts = {}
            sentiment_counts = {}
            urgency_counts = {}
            total_duration = 0
            total_messages = 0
            
            for result in results:
                if 'error' not in result:
                    intent = result['intent']
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
                    total_duration += result.get('duration_seconds', 0)
                    total_messages += result.get('message_count', 0)
                    
                    # ML-specific insights
                    if 'sentiment' in result:
                        sentiment = result['sentiment']
                        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                    
                    if 'urgency' in result:
                        urgency = result['urgency']
                        urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            print("Intent Distribution:")
            for intent, count in sorted(intent_counts.items()):
                percentage = (count / successful_processes) * 100
                print(f"  {intent}: {count} ({percentage:.1f}%)")
            
            # Show sentiment distribution if available
            if sentiment_counts:
                print("\nSentiment Distribution:")
                for sentiment, count in sorted(sentiment_counts.items()):
                    percentage = (count / successful_processes) * 100
                    print(f"  {sentiment}: {count} ({percentage:.1f}%)")
            
            # Show urgency distribution if available
            if urgency_counts:
                print("\nUrgency Distribution:")
                for urgency, count in sorted(urgency_counts.items()):
                    percentage = (count / successful_processes) * 100
                    print(f"  {urgency}: {count} ({percentage:.1f}%)")
            
            if successful_processes > 0:
                avg_duration = total_duration / successful_processes
                avg_messages = total_messages / successful_processes
                print(f"\nAverage thread duration: {avg_duration:.1f}s")
                print(f"Average messages per thread: {avg_messages:.1f}")
        
        print("\n" + "=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        
        # Save results if requested
        output_file = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    main() 