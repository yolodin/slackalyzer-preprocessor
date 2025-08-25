#!/usr/bin/env python3
"""
Startup script for Hermes Dashboard.
Runs both the Python API backend and React frontend.
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_python_api():
    """Run the Python Flask API server."""
    print("🚀 Starting Python API server...")
    try:
        # Install Python dependencies if needed
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"], 
                      check=True, capture_output=True)
        
        # Run the API server from src/web directory
        web_api_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'web', 'web_api.py')
        os.execv(sys.executable, [sys.executable, web_api_path])
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Python dependencies: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Python API: {e}")
        sys.exit(1)

def run_nextjs_frontend():
    """Run the Next.js frontend development server."""
    print("🎨 Starting Next.js frontend...")
    
    web_dir = Path("web-dashboard")
    if not web_dir.exists():
        print("❌ Web dashboard directory not found!")
        sys.exit(1)
    
    try:
        # Change to web directory
        os.chdir(web_dir)
        
        # Install Node.js dependencies
        print("📦 Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], check=True)
        
        # Start Next.js development server
        print("✅ Starting Next.js development server...")
        os.execv("npm", ["npm", "run", "dev"])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error with Node.js setup: {e}")
        print("Make sure Node.js and npm are installed!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Next.js frontend: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    # Check Python
    try:
        subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
        print("✅ Python is available")
    except subprocess.CalledProcessError:
        print("❌ Python is not available")
        return False
    
    # Check Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js is available")
    except subprocess.CalledProcessError:
        print("❌ Node.js is not available. Please install Node.js first.")
        return False
    
    # Check npm
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        print("✅ npm is available")
    except subprocess.CalledProcessError:
        print("❌ npm is not available. Please install npm first.")
        return False
    
    return True

def setup_data():
    """Set up initial data if needed."""
    print("📊 Setting up initial data...")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Check if standardized data exists
    standardized_data = data_dir / "standardized_slack_data.json"
    if not standardized_data.exists():
        print("⚠️  No standardized data found. Running data adapter...")
        try:
            adapter_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'slackops', 'slack_data_adapter.py')
            subprocess.run([sys.executable, adapter_path, "--setup"], 
                          check=True, capture_output=True)
            print("✅ Data adapter completed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Data adapter failed: {e}")
            print("You can manually run: python src/slackops/slack_data_adapter.py --setup")
    else:
        print("✅ Standardized data found")

def main():
    """Main function to orchestrate the startup."""
    print("=" * 60)
    print("🔧 Hermes Communication Intelligence Dashboard")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup data
    setup_data()
    
    # Get the startup mode
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("\n📋 Select startup mode:")
        print("1. Full stack (API + Frontend)")
        print("2. API only")
        print("3. Frontend only")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            mode = "full"
        elif choice == "2":
            mode = "api"
        elif choice == "3":
            mode = "frontend"
        else:
            print("Invalid choice. Starting full stack...")
            mode = "full"
    
    print(f"\n🚀 Starting in {mode} mode...")
    
    if mode == "full":
        print("\n📡 Starting Python API server in background...")
        web_api_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'web', 'web_api.py')
        api_process = subprocess.Popen([sys.executable, web_api_path])
        
        # Give the API server time to start
        time.sleep(3)
        
        print("🎨 Starting Next.js frontend...")
        try:
            os.chdir("web-dashboard")
            subprocess.run(["npm", "install"], check=True)
            subprocess.run(["npm", "run", "dev"], check=True)
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down...")
            api_process.terminate()
            api_process.wait()
        except Exception as e:
            print(f"❌ Error: {e}")
            api_process.terminate()
            api_process.wait()
            sys.exit(1)
    
    elif mode == "api":
        run_python_api()
    
    elif mode == "frontend":
        run_nextjs_frontend()
    
    else:
        print("❌ Invalid mode. Use 'full', 'api', or 'frontend'")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 