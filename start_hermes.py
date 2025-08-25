#!/usr/bin/env python3
"""
🚀 Hermes Communication Intelligence System Startup Script
Comprehensive launcher for the complete Hermes platform.
"""

import os
import sys
import subprocess
import time
import threading
import signal
import webbrowser
from pathlib import Path
import argparse

# Global process references for cleanup
api_process = None
frontend_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n🛑 Shutdown signal received...")
    cleanup_processes()
    print("👋 Hermes shutdown complete!")
    sys.exit(0)

def cleanup_processes():
    """Clean up running processes."""
    global api_process, frontend_process
    
    if api_process:
        print("⏹️  Stopping API server...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
    
    if frontend_process:
        print("⏹️  Stopping frontend server...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking system dependencies...")
    
    issues = []
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        python_version = result.stdout.strip()
        print(f"✅ {python_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("❌ Python is not available or not working properly")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js {node_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("❌ Node.js is not installed. Please install from https://nodejs.org/")
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], 
                              capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        print(f"✅ npm {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("❌ npm is not available")
    
    if issues:
        print("\n🚨 Dependency Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    requirements_files = ["requirements_web.txt", "requirements.txt"]
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            try:
                print(f"   Installing from {req_file}...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Failed to install from {req_file}: {e}")
                print("   Continuing anyway...")
    
    print("✅ Python dependencies installation completed")

def install_frontend_dependencies():
    """Install frontend dependencies."""
    print("📦 Installing frontend dependencies...")
    
    web_dir = Path("web-dashboard")
    if not web_dir.exists():
        print("❌ Web dashboard directory not found!")
        return False
    
    original_dir = os.getcwd()
    try:
        os.chdir(web_dir)
        
        # Check if node_modules exists and package.json is newer
        package_json = Path("package.json")
        node_modules = Path("node_modules")
        
        if not node_modules.exists() or (package_json.exists() and 
            package_json.stat().st_mtime > node_modules.stat().st_mtime):
            print("   Running npm install...")
            subprocess.run(["npm", "install"], check=True)
        else:
            print("   Dependencies already up to date")
        
        print("✅ Frontend dependencies ready")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error installing frontend dependencies: {e}")
        return False
    finally:
        os.chdir(original_dir)

def setup_data():
    """Set up initial data if needed."""
    print("📊 Preparing data...")
    
    # Create necessary directories
    for directory in ["data", "results", "reports", "models"]:
        Path(directory).mkdir(exist_ok=True)
    
    # Check for data files
    data_dir = Path("data")
    data_files = list(data_dir.glob("*.json"))
    
    if not data_files:
        print("⚠️  No data files found in data/ directory")
        print("   You can add Slack export files to the data/ directory")
    else:
        print(f"✅ Found {len(data_files)} data files")
    
    # Run data adapter if needed
    standardized_data = data_dir / "standardized_slack_data.json"
    if not standardized_data.exists() and data_files:
        print("🔄 Running data standardization...")
        try:
            adapter_script = Path("src/slackops/slack_data_adapter.py")
            if adapter_script.exists():
                subprocess.run([sys.executable, str(adapter_script), "--setup"], 
                             check=True, capture_output=True)
                print("✅ Data standardization completed")
            else:
                print("⚠️  Data adapter not found, skipping standardization")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Data standardization failed: {e}")
            print("   You can run it manually later")

def start_api_server():
    """Start the Python API server."""
    global api_process
    
    print("🐍 Starting Hermes API server...")
    
    api_script = Path("src/web/web_api.py")
    if not api_script.exists():
        print("❌ API server script not found!")
        return None
    
    try:
        api_process = subprocess.Popen(
            [sys.executable, str(api_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the server time to start
        time.sleep(3)
        
        # Check if the process is still running
        if api_process.poll() is None:
            print("✅ API server started successfully on http://localhost:8000")
            return api_process
        else:
            stdout, stderr = api_process.communicate()
            print(f"❌ API server failed to start:")
            if stderr:
                print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_frontend_server():
    """Start the frontend development server."""
    global frontend_process
    
    print("⚛️  Starting Hermes frontend...")
    
    web_dir = Path("web-dashboard")
    if not web_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    original_dir = os.getcwd()
    try:
        os.chdir(web_dir)
        
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the server time to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend started successfully on http://localhost:3000")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend failed to start:")
            if stderr:
                print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None
    finally:
        os.chdir(original_dir)

def wait_for_servers():
    """Wait for servers to be ready and open browser."""
    print("⏳ Waiting for servers to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            # Check API health
            import urllib.request
            urllib.request.urlopen("http://localhost:8000/api/health", timeout=1)
            
            # Check frontend
            urllib.request.urlopen("http://localhost:3000", timeout=1)
            
            print("🎉 All servers are ready!")
            print("\n" + "="*60)
            print("🚀 HERMES IS NOW RUNNING!")
            print("="*60)
            print("📊 Dashboard: http://localhost:3000")
            print("🔌 API:       http://localhost:8000")
            print("📚 API Docs:  http://localhost:8000/api/health")
            print("="*60)
            
            # Open browser
            try:
                webbrowser.open("http://localhost:3000")
                print("🌐 Browser opened automatically")
            except:
                print("🌐 Please open http://localhost:3000 in your browser")
            
            return True
            
        except:
            time.sleep(1)
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
    
    print("⚠️  Servers may not be fully ready, but you can try accessing them")
    return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Start the Hermes Communication Intelligence System")
    parser.add_argument("--mode", choices=["full", "api", "frontend"], 
                       default="full", help="Startup mode")
    parser.add_argument("--no-browser", action="store_true", 
                       help="Don't open browser automatically")
    parser.add_argument("--dev", action="store_true", 
                       help="Development mode with verbose output")
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🌟" * 30)
    print("🚀 HERMES COMMUNICATION INTELLIGENCE SYSTEM")
    print("🌟" * 30)
    print("Named after the Greek god of communication")
    print("AI-Powered Slack Analysis & Insights Platform")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Install dependencies
    if args.mode in ["full", "api"]:
        install_python_dependencies()
    
    if args.mode in ["full", "frontend"]:
        if not install_frontend_dependencies():
            sys.exit(1)
    
    # Setup data
    if args.mode in ["full", "api"]:
        setup_data()
    
    # Start services
    try:
        if args.mode == "full":
            # Start both API and frontend
            api_proc = start_api_server()
            if not api_proc:
                print("❌ Failed to start API server")
                sys.exit(1)
            
            frontend_proc = start_frontend_server()
            if not frontend_proc:
                print("❌ Failed to start frontend server")
                cleanup_processes()
                sys.exit(1)
            
            # Wait for servers and open browser
            if not args.no_browser:
                wait_for_servers()
            
            print("\n💡 Press Ctrl+C to stop all servers")
            
            # Keep the main process alive
            try:
                while True:
                    if api_process and api_process.poll() is not None:
                        print("❌ API server stopped unexpectedly")
                        break
                    if frontend_process and frontend_process.poll() is not None:
                        print("❌ Frontend server stopped unexpectedly")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        elif args.mode == "api":
            api_proc = start_api_server()
            if api_proc:
                print("\n💡 Press Ctrl+C to stop the API server")
                try:
                    api_proc.wait()
                except KeyboardInterrupt:
                    pass
            
        elif args.mode == "frontend":
            frontend_proc = start_frontend_server()
            if frontend_proc:
                print("\n💡 Press Ctrl+C to stop the frontend server")
                try:
                    frontend_proc.wait()
                except KeyboardInterrupt:
                    pass
    
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main()
