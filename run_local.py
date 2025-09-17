
"""
Local development server runner for Student Engagement API
"""
import os
import sys
import subprocess
import time
import requests
import threading

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import tensorflow
        import PIL
        import numpy
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_model_file():
    """Check if model file exists"""
    model_path = "Student_Engagement_Model.h5"
    if os.path.exists(model_path):
        print(f"✓ Model file found: {model_path}")
        return True
    else:
        print(f"✗ Model file not found: {model_path}")
        print("Please ensure the model file is in the current directory")
        return False

def start_server():
    """Start the Flask development server"""
    print("Starting Flask development server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the Flask app
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Server failed to start: {e}")

def wait_for_server(url, timeout=60):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def run_tests_after_startup():
    """Run tests after server starts"""
    time.sleep(5)  # Wait a bit for server to fully start
    if wait_for_server('http://localhost:5000', timeout=30):
        print("\n" + "="*50)
        print("SERVER IS READY! Running tests...")
        print("="*50)
        try:
            subprocess.run([sys.executable, 'test_api.py'], check=True)
        except subprocess.CalledProcessError:
            print("Tests failed - but server is still running")
    else:
        print("Server not responding - tests skipped")

def main():
    print("Student Engagement API - Local Development Server")
    print("=" * 50)
    
    # Check prerequisites
    if not check_dependencies():
        return 1
        
    if not check_model_file():
        return 1
    
    # Ask if user wants to run tests
    run_tests = input("\nRun tests after server starts? (y/n): ").lower().strip() == 'y'
    
    if run_tests:
        # Start test thread
        test_thread = threading.Thread(target=run_tests_after_startup)
        test_thread.daemon = True
        test_thread.start()
    
    # Start server
    start_server()
    return 0

if __name__ == "__main__":
    sys.exit(main())