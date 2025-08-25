#!/usr/bin/env python3
"""
Slack Data Adapter for Hermes Communication Intelligence System.

This adapter handles various Slack export formats and converts them
to the standardized format expected by the AI pipeline without modifying
any existing code.
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import re
from dateutil import parser as date_parser


class SlackDataAdapter:
    """
    Adapter for converting various Slack export formats to the standard pipeline format.
    """
    
    def __init__(self, data_directory: str = "data/"):
        """
        Initialize the Slack data adapter.
        
        Args:
            data_directory: Directory containing Slack export files
        """
        self.data_directory = data_directory
        self.supported_formats = [
            "thread_export",      # Pre-formatted thread data
            "channel_export",     # Raw channel exports
            "slack_archive",      # Full Slack workspace exports
            "custom_format"       # User-defined formats
        ]
        
    def detect_format(self, file_path: str) -> str:
        """
        Automatically detect the format of a Slack export file.
        
        Args:
            file_path: Path to the Slack export file
            
        Returns:
            Detected format type
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list) or not data:
                return "unknown"
            
            sample = data[0]
            
            # Check for thread export format (has thread_ts and messages)
            if "thread_ts" in sample and "messages" in sample:
                return "thread_export"
            
            # Check for channel export format (direct message list)
            if "ts" in sample and "text" in sample and "user" in sample:
                return "channel_export"
            
            # Check for custom format with timestamp field
            if "messages" in sample and isinstance(sample["messages"], list):
                if sample["messages"] and "timestamp" in sample["messages"][0]:
                    return "custom_format"
            
            return "unknown"
            
        except Exception as e:
            print(f"Error detecting format for {file_path}: {e}")
            return "unknown"
    
    def normalize_timestamp(self, timestamp: Union[str, float, int]) -> str:
        """
        Normalize various timestamp formats to Unix timestamp string.
        
        Args:
            timestamp: Timestamp in various formats
            
        Returns:
            Normalized Unix timestamp string
        """
        try:
            # If already a Unix timestamp
            if isinstance(timestamp, (int, float)):
                return str(timestamp)
            
            # If string representation of Unix timestamp
            if isinstance(timestamp, str) and timestamp.replace('.', '').isdigit():
                return timestamp
            
            # If ISO format or other date string
            if isinstance(timestamp, str):
                dt = date_parser.parse(timestamp)
                return str(dt.timestamp())
                
        except Exception as e:
            print(f"Warning: Could not normalize timestamp {timestamp}: {e}")
            # Return current time as fallback
            return str(datetime.now().timestamp())
        
        return str(datetime.now().timestamp())
    
    def convert_thread_export(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert thread export format to standard format.
        
        Args:
            data: Raw thread export data
            
        Returns:
            Standardized thread data
        """
        standardized = []
        
        for thread in data:
            # Handle different thread ID fields
            thread_id = thread.get('thread_ts', thread.get('thread_id', 'unknown'))
            
            # Process messages
            messages = []
            for msg in thread.get('messages', []):
                # Normalize timestamp field names
                ts = msg.get('ts') or msg.get('timestamp') or msg.get('time')
                ts = self.normalize_timestamp(ts)
                
                # Clean and format message
                standardized_msg = {
                    'ts': ts,
                    'user': msg.get('user', msg.get('username', 'unknown')),
                    'text': self._clean_message_text(msg.get('text', ''))
                }
                
                # Add optional fields if present
                if 'reactions' in msg:
                    standardized_msg['reactions'] = msg['reactions']
                if 'replies' in msg:
                    standardized_msg['replies'] = msg['replies']
                
                messages.append(standardized_msg)
            
            # Sort messages by timestamp
            messages.sort(key=lambda m: float(m['ts']))
            
            standardized_thread = {
                'thread_ts': thread_id,
                'messages': messages
            }
            
            # Add optional metadata
            if 'channel' in thread:
                standardized_thread['channel'] = thread['channel']
            if 'priority' in thread:
                standardized_thread['priority'] = thread['priority']
            
            standardized.append(standardized_thread)
        
        return standardized
    
    def convert_channel_export(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert channel export format to thread-based format.
        
        Args:
            data: Raw channel export data (list of messages)
            
        Returns:
            Standardized thread data
        """
        # Group messages into threads
        threads = {}
        
        for msg in data:
            # Determine thread ID
            thread_id = msg.get('thread_ts') or msg.get('ts')
            
            if thread_id not in threads:
                threads[thread_id] = []
            
            # Normalize message
            normalized_msg = {
                'ts': self.normalize_timestamp(msg.get('ts')),
                'user': msg.get('user', 'unknown'),
                'text': self._clean_message_text(msg.get('text', ''))
            }
            
            threads[thread_id].append(normalized_msg)
        
        # Convert to standard format
        standardized = []
        for thread_id, messages in threads.items():
            # Sort messages by timestamp
            messages.sort(key=lambda m: float(m['ts']))
            
            # Only include threads with multiple messages or substantial content
            if len(messages) > 1 or (len(messages) == 1 and len(messages[0]['text']) > 20):
                standardized.append({
                    'thread_ts': thread_id,
                    'messages': messages
                })
        
        return standardized
    
    def convert_custom_format(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert custom format with flexible field mapping.
        
        Args:
            data: Raw data in custom format
            
        Returns:
            Standardized thread data
        """
        standardized = []
        
        for thread in data:
            # Extract thread ID with fallbacks
            thread_id = (thread.get('thread_ts') or 
                        thread.get('id') or 
                        thread.get('thread_id') or 
                        f"thread_{len(standardized)}")
            
            # Process messages with flexible field mapping
            messages = []
            for msg in thread.get('messages', []):
                # Handle different timestamp formats
                ts = (msg.get('ts') or 
                     msg.get('timestamp') or 
                     msg.get('time') or 
                     msg.get('created_at'))
                
                ts = self.normalize_timestamp(ts)
                
                # Handle different user field names
                user = (msg.get('user') or 
                       msg.get('username') or 
                       msg.get('author') or 
                       msg.get('sender') or 
                       'unknown')
                
                # Handle different text field names
                text = (msg.get('text') or 
                       msg.get('message') or 
                       msg.get('content') or 
                       msg.get('body') or 
                       '')
                
                messages.append({
                    'ts': ts,
                    'user': str(user),
                    'text': self._clean_message_text(text)
                })
            
            # Sort and add thread
            messages.sort(key=lambda m: float(m['ts']))
            
            if messages:  # Only add non-empty threads
                standardized_thread = {
                    'thread_ts': str(thread_id),
                    'messages': messages
                }
                
                # Preserve additional metadata
                for key in ['channel', 'priority', 'category', 'tags']:
                    if key in thread:
                        standardized_thread[key] = thread[key]
                
                standardized.append(standardized_thread)
        
        return standardized
    
    def _clean_message_text(self, text: str) -> str:
        """
        Clean and normalize message text.
        
        Args:
            text: Raw message text
            
        Returns:
            Cleaned message text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove Slack formatting
        text = re.sub(r'<@\w+>', '@user', text)  # Replace user mentions
        text = re.sub(r'<#\w+\|([^>]+)>', r'#\1', text)  # Replace channel mentions
        text = re.sub(r'<(https?://[^>|]+)>', r'\1', text)  # Clean URLs
        text = re.sub(r'<([^>|]+)\|([^>]+)>', r'\2', text)  # Replace link formatting
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def load_slack_data(self, file_pattern: str = "*.json", 
                       format_override: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load and convert Slack data from files.
        
        Args:
            file_pattern: Glob pattern for files to load
            format_override: Force a specific format instead of auto-detection
            
        Returns:
            Standardized thread data ready for pipeline processing
        """
        all_threads = []
        
        # Find all matching files
        search_pattern = os.path.join(self.data_directory, file_pattern)
        files = glob.glob(search_pattern)
        
        if not files:
            print(f"No files found matching pattern: {search_pattern}")
            return []
        
        print(f"Found {len(files)} Slack data files")
        
        for file_path in files:
            print(f"Processing: {os.path.basename(file_path)}")
            
            try:
                # Load raw data
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                if not isinstance(raw_data, list):
                    print(f"Warning: {file_path} does not contain a list, skipping")
                    continue
                
                # Detect or use override format
                if format_override:
                    detected_format = format_override
                else:
                    detected_format = self.detect_format(file_path)
                
                print(f"  Format: {detected_format}")
                
                # Convert based on format
                if detected_format == "thread_export":
                    converted = self.convert_thread_export(raw_data)
                elif detected_format == "channel_export":
                    converted = self.convert_channel_export(raw_data)
                elif detected_format == "custom_format":
                    converted = self.convert_custom_format(raw_data)
                else:
                    print(f"  Warning: Unknown format, trying custom format converter")
                    converted = self.convert_custom_format(raw_data)
                
                print(f"  Converted {len(converted)} threads")
                all_threads.extend(converted)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        print(f"Total threads loaded: {len(all_threads)}")
        return all_threads
    
    def save_standardized_data(self, threads: List[Dict[str, Any]], 
                              output_file: str = "standardized_slack_data.json"):
        """
        Save standardized thread data to file.
        
        Args:
            threads: Standardized thread data
            output_file: Output file path
        """
        output_path = os.path.join(self.data_directory, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(threads, f, indent=2, ensure_ascii=False)
        
        print(f"Standardized data saved to: {output_path}")
    
    def validate_data(self, threads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the standardized thread data.
        
        Args:
            threads: Thread data to validate
            
        Returns:
            Validation report
        """
        report = {
            'total_threads': len(threads),
            'total_messages': 0,
            'unique_users': set(),
            'date_range': {'earliest': None, 'latest': None},
            'issues': []
        }
        
        timestamps = []
        
        for i, thread in enumerate(threads):
            if 'thread_ts' not in thread:
                report['issues'].append(f"Thread {i}: Missing thread_ts")
                continue
            
            if 'messages' not in thread or not thread['messages']:
                report['issues'].append(f"Thread {i}: No messages")
                continue
            
            for j, msg in enumerate(thread['messages']):
                report['total_messages'] += 1
                
                # Check required fields
                for field in ['ts', 'user', 'text']:
                    if field not in msg:
                        report['issues'].append(f"Thread {i}, Message {j}: Missing {field}")
                
                # Collect user info
                if 'user' in msg:
                    report['unique_users'].add(msg['user'])
                
                # Collect timestamps
                if 'ts' in msg:
                    try:
                        timestamps.append(float(msg['ts']))
                    except ValueError:
                        report['issues'].append(f"Thread {i}, Message {j}: Invalid timestamp")
        
        # Calculate date range
        if timestamps:
            report['date_range']['earliest'] = datetime.fromtimestamp(min(timestamps))
            report['date_range']['latest'] = datetime.fromtimestamp(max(timestamps))
        
        report['unique_users'] = len(report['unique_users'])
        
        return report


def create_adapter_config(data_directory: str = "data/") -> Dict[str, Any]:
    """
    Create a configuration file for the Slack data adapter.
    
    Args:
        data_directory: Directory containing Slack data
        
    Returns:
        Configuration dictionary
    """
    config = {
        "data_directory": data_directory,
        "file_patterns": {
            "all_json": "*.json",
            "slack_exports": "slack_export*.json",
            "channels": "channel_*.json",
            "threads": "thread_*.json"
        },
        "format_mappings": {
            "custom_field_mapping": {
                "timestamp_fields": ["ts", "timestamp", "time", "created_at"],
                "user_fields": ["user", "username", "author", "sender"],
                "text_fields": ["text", "message", "content", "body"],
                "thread_id_fields": ["thread_ts", "id", "thread_id"]
            }
        },
        "filtering": {
            "min_messages_per_thread": 1,
            "min_text_length": 10,
            "exclude_bots": True,
            "exclude_system_messages": True
        },
        "output": {
            "standardized_file": "standardized_slack_data.json",
            "validation_report": "../reports/data_validation_report.json"
        }
    }
    
    config_path = os.path.join("config", "adapter_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Adapter configuration saved to: {config_path}")
    return config


# Convenience functions for easy integration
def load_and_convert_slack_data(data_directory: str = "data/", 
                               file_pattern: str = "*.json") -> List[Dict[str, Any]]:
    """
    Convenience function to load and convert Slack data in one step.
    
    Args:
        data_directory: Directory containing Slack data files
        file_pattern: Pattern to match files
        
    Returns:
        Standardized thread data ready for pipeline
    """
    adapter = SlackDataAdapter(data_directory)
    return adapter.load_slack_data(file_pattern)


def quick_setup(data_directory: str = "data/") -> str:
    """
    Quick setup for new users.
    
    Args:
        data_directory: Directory containing Slack data
        
    Returns:
        Path to standardized data file
    """
    print("=" * 60)
    print("SLACK DATA ADAPTER - QUICK SETUP")
    print("=" * 60)
    
    # Create adapter
    adapter = SlackDataAdapter(data_directory)
    
    # Create configuration
    config = create_adapter_config(data_directory)
    
    # Load and convert data
    threads = adapter.load_slack_data()
    
    if not threads:
        print("No data found. Please check your data directory and file formats.")
        return ""
    
    # Validate data
    validation_report = adapter.validate_data(threads)
    print(f"\nValidation Report:")
    print(f"  Total threads: {validation_report['total_threads']}")
    print(f"  Total messages: {validation_report['total_messages']}")
    print(f"  Unique users: {validation_report['unique_users']}")
    if validation_report['date_range']['earliest']:
        print(f"  Date range: {validation_report['date_range']['earliest'].date()} to {validation_report['date_range']['latest'].date()}")
    
    if validation_report['issues']:
        print(f"  Issues found: {len(validation_report['issues'])}")
        for issue in validation_report['issues'][:5]:  # Show first 5 issues
            print(f"    - {issue}")
        if len(validation_report['issues']) > 5:
            print(f"    ... and {len(validation_report['issues']) - 5} more")
    
    # Save standardized data
    output_file = "standardized_slack_data.json"
    adapter.save_standardized_data(threads, output_file)
    
    # Save validation report
    validation_path = os.path.join("reports", "data_validation_report.json")
    with open(validation_path, 'w') as f:
        json.dump(validation_report, f, indent=2, default=str)
    
    print(f"\nSetup complete! Use this file with the pipeline:")
    print(f"python3 run_pipeline_ml.py --data-file {os.path.join(data_directory, output_file)}")
    
    return os.path.join(data_directory, output_file)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Slack Data Adapter")
    parser.add_argument("--setup", action="store_true", help="Run quick setup")
    parser.add_argument("--data-dir", default="data/", help="Data directory")
    parser.add_argument("--pattern", default="*.json", help="File pattern")
    parser.add_argument("--format", help="Force specific format")
    
    args = parser.parse_args()
    
    if args.setup:
        quick_setup(args.data_dir)
    else:
        adapter = SlackDataAdapter(args.data_dir)
        threads = adapter.load_slack_data(args.pattern, args.format)
        
        if threads:
            adapter.save_standardized_data(threads)
            print(f"Converted {len(threads)} threads successfully!")
        else:
            print("No data converted. Check your files and formats.") 