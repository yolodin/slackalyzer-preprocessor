#!/usr/bin/env python3
"""
Web API bridge for Hermes Communication Intelligence System.
Provides REST API endpoints for the React dashboard.
"""

import json
import os
import sys
import threading
import time
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our modules
from slackops import preprocess
from slackops import summarize
from slackops import classify
from slackops import slack_data_adapter

# Import scripts
scripts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
sys.path.insert(0, scripts_path)

try:
    import run_pipeline
    import run_pipeline_ml
except ImportError as e:
    logger.error(f"Failed to import pipeline modules: {e}")
    # Define ML_AVAILABLE as fallback
    class MockML:
        ML_AVAILABLE = False
    run_pipeline_ml = MockML()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for processing
processing_state = {
    'is_processing': False,
    'current_thread': None,
    'progress': 0,
    'total_threads': 0,
    'results': [],
    'errors': [],
    'start_time': None,
    'end_time': None,
    'processing_method': 'rule-based'
}

# Store processed results
processed_results = []
system_stats = {
    'total_processed': 0,
    'success_rate': 0.0,
    'average_processing_time': 0.0,
    'last_processed': None
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get current system status."""
    return jsonify({
        'processing': processing_state['is_processing'],
        'stats': system_stats,
        'ml_available': run_pipeline_ml.ML_AVAILABLE,
        'data_files': get_available_data_files()
    })

@app.route('/api/data/files', methods=['GET'])
def get_data_files():
    """Get list of available data files."""
    files = get_available_data_files()
    return jsonify({'files': files})

@app.route('/api/data/validation', methods=['GET'])
def get_validation_report():
    """Get data validation report."""
    try:
        validation_path = os.path.join("reports", "data_validation_report.json")
        if os.path.exists(validation_path):
            with open(validation_path, 'r') as f:
                report = json.load(f)
            return jsonify(report)
        else:
            # Return empty report if file doesn't exist
            return jsonify({
                'total_threads': 0,
                'total_messages': 0,
                'unique_users': 0,
                'date_range': {'earliest': None, 'latest': None},
                'issues': []
            })
    except Exception as e:
        logger.error(f"Error reading validation report: {e}")
        return jsonify({
            'total_threads': 0,
            'total_messages': 0,
            'unique_users': 0,
            'date_range': {'earliest': None, 'latest': None},
            'issues': []
        }), 500

@app.route('/api/data/upload', methods=['POST'])
def upload_data():
    """Upload new data file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.json'):
        filename = f"data/{file.filename}"
        file.save(filename)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/processing/start', methods=['POST'])
def start_processing():
    """Start processing Slack data."""
    global processing_state
    
    if processing_state['is_processing']:
        return jsonify({'error': 'Processing already in progress'}), 400
    
    data = request.json
    data_file = data.get('data_file', 'data/standardized_slack_data.json')
    use_ml = data.get('use_ml', False)
    use_lightweight = data.get('use_lightweight', True)
    max_threads = data.get('max_threads', None)
    
    # Reset processing state
    processing_state.update({
        'is_processing': True,
        'current_thread': None,
        'progress': 0,
        'total_threads': 0,
        'results': [],
        'errors': [],
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'processing_method': 'ML' if use_ml else 'rule-based'
    })
    
    # Start processing in background thread
    thread = threading.Thread(
        target=process_data_async,
        args=(data_file, use_ml, use_lightweight, max_threads)
    )
    thread.start()
    
    return jsonify({'message': 'Processing started', 'job_id': int(time.time())})

@app.route('/api/processing/status', methods=['GET'])
def get_processing_status():
    """Get current processing status."""
    return jsonify(processing_state)

@app.route('/api/processing/stop', methods=['POST'])
def stop_processing():
    """Stop current processing."""
    global processing_state
    processing_state['is_processing'] = False
    processing_state['end_time'] = datetime.now().isoformat()
    return jsonify({'message': 'Processing stopped'})

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get processing results with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_results = processed_results[start:end]
    
    return jsonify({
        'results': paginated_results,
        'total': len(processed_results),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(processed_results) + per_page - 1) // per_page
    })

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary."""
    if not processed_results:
        return jsonify({
            'total_threads': 0,
            'intents': {},
            'sentiment': {},
            'urgency': {},
            'processing_times': []
        })
    
    # Analyze results
    intents = {}
    sentiment = {}
    urgency = {}
    processing_times = []
    
    for result in processed_results:
        # Count intents
        intent = result.get('intent', 'unknown')
        intents[intent] = intents.get(intent, 0) + 1
        
        # Count sentiment if available
        if 'sentiment' in result:
            sent = result['sentiment']
            sentiment[sent] = sentiment.get(sent, 0) + 1
        
        # Count urgency if available
        if 'urgency' in result:
            urg = result['urgency']
            urgency[urg] = urgency.get(urg, 0) + 1
        
        # Processing time
        if 'processing_time' in result:
            processing_times.append(result['processing_time'])
    
    return jsonify({
        'total_threads': len(processed_results),
        'intents': intents,
        'sentiment': sentiment,
        'urgency': urgency,
        'processing_times': processing_times,
        'avg_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0
    })

@app.route('/api/analytics/recent', methods=['GET'])
def get_recent_activity():
    """Get recent processing activity."""
    limit = request.args.get('limit', 10, type=int)
    recent_results = processed_results[-limit:] if processed_results else []
    
    return jsonify({
        'recent_results': recent_results,
        'count': len(recent_results)
    })

@app.route('/api/ml/models', methods=['GET'])
def get_ml_models():
    """Get information about available ML models."""
    return jsonify({
        'available': run_pipeline_ml.ML_AVAILABLE,
        'models': {
            'classification': {
                'transformer': 'DistilBERT',
                'lightweight': 'MiniLM + Random Forest'
            },
            'summarization': {
                'abstractive': 'BART-large-CNN',
                'extractive': 'Sentence Embeddings'
            }
        }
    })

def get_available_data_files():
    """Get list of available data files."""
    data_dir = 'data'
    if not os.path.exists(data_dir):
        return []
    
    files = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(data_dir, filename)
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

def update_validation_report(threads: List[Dict[str, Any]]):
    """Update the validation report with processed data metrics."""
    try:
        # Calculate metrics from processed threads
        total_threads = len(threads)
        total_messages = 0
        unique_users = set()
        timestamps = []
        
        for thread in threads:
            messages = thread.get('messages', [])
            total_messages += len(messages)
            
            for msg in messages:
                if 'user' in msg:
                    unique_users.add(msg['user'])
                if 'ts' in msg:
                    try:
                        timestamps.append(float(msg['ts']))
                    except ValueError:
                        pass
        
        # Calculate date range
        date_range = {'earliest': None, 'latest': None}
        if timestamps:
            earliest = datetime.fromtimestamp(min(timestamps))
            latest = datetime.fromtimestamp(max(timestamps))
            date_range = {
                'earliest': earliest.isoformat(),
                'latest': latest.isoformat()
            }
        
        # Create updated report
        validation_report = {
            'total_threads': total_threads,
            'total_messages': total_messages,
            'unique_users': len(unique_users),
            'date_range': date_range,
            'issues': []
        }
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        # Save updated validation report
        validation_path = os.path.join('reports', 'data_validation_report.json')
        with open(validation_path, 'w') as f:
            json.dump(validation_report, f, indent=2)
        
        logger.info(f"Updated validation report: {total_threads} threads, {total_messages} messages, {len(unique_users)} users")
        
    except Exception as e:
        logger.error(f"Error updating validation report: {e}")

def process_data_async(data_file: str, use_ml: bool, use_lightweight: bool, max_threads: int):
    """Process data in background thread."""
    global processing_state, processed_results, system_stats
    
    try:
        # Load data
        threads = run_pipeline_ml.load_slack_export(data_file)
        
        if max_threads:
            threads = threads[:max_threads]
        
        processing_state['total_threads'] = len(threads)
        
        # Initialize ML models if needed
        if use_ml:
            if not run_pipeline_ml.initialize_ml_models(use_lightweight):
                use_ml = False
                processing_state['processing_method'] = 'rule-based (ML failed)'
        
        # Process threads
        results = []
        for i, thread in enumerate(threads):
            if not processing_state['is_processing']:
                break
            
            processing_state['current_thread'] = thread.get('thread_ts', f'thread_{i}')
            processing_state['progress'] = i + 1
            
            start_time = time.time()
            try:
                result = run_pipeline_ml.process_single_thread(
                    thread, use_ml=use_ml, use_lightweight=use_lightweight
                )
                result['processing_time'] = time.time() - start_time
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing thread {i}: {e}")
                processing_state['errors'].append(f"Thread {i}: {str(e)}")
        
        # Update global state
        processed_results.extend(results)
        processing_state['results'] = results
        processing_state['is_processing'] = False
        processing_state['end_time'] = datetime.now().isoformat()
        
        # Update system stats
        system_stats['total_processed'] += len(results)
        system_stats['success_rate'] = (len(results) / len(threads)) * 100
        system_stats['last_processed'] = datetime.now().isoformat()
        
        if results:
            avg_time = sum(r.get('processing_time', 0) for r in results) / len(results)
            system_stats['average_processing_time'] = avg_time
        
        # Update validation report with processed data metrics
        update_validation_report(threads)
        
        logger.info(f"Processing completed: {len(results)} threads processed")
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        processing_state['is_processing'] = False
        processing_state['errors'].append(str(e))
        processing_state['end_time'] = datetime.now().isoformat()

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Start the API server
    app.run(host='0.0.0.0', port=8000, debug=True) 