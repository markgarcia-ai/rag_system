#!/usr/bin/env python3
"""
RAG System Startup Script
Handles package compatibility and dynamic port allocation
"""

import subprocess
import sys
import os
from pathlib import Path

def check_and_fix_packages():
    """Check and fix package compatibility issues"""
    print("🔍 Checking package compatibility...")
    
    try:
        import sentence_transformers
        print("✅ sentence_transformers is available")
    except ImportError as e:
        print(f"❌ sentence_transformers import error: {e}")
        print("📦 Installing/upgrading packages...")
        
        # Upgrade packages to fix compatibility
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--upgrade", "huggingface_hub", "sentence_transformers"
        ], check=True)
        
        print("✅ Packages upgraded successfully")

def start_server():
    """Start the RAG system server"""
    print("🚀 Starting RAG System...")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    main_py = script_dir / "main.py"
    
    if not main_py.exists():
        print(f"❌ main.py not found at {main_py}")
        return False
    
    try:
        # Start the server
        subprocess.run([sys.executable, str(main_py)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True

def main():
    """Main function"""
    print("=" * 60)
    print("🤖 RAG System Startup")
    print("=" * 60)
    
    # Check and fix packages
    check_and_fix_packages()
    
    # Start server
    success = start_server()
    
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're in the virtual environment: source venv/bin/activate")
        print("2. Check if port 5000 is in use: lsof -i :5000")
        print("3. Try manually: python main.py")
        print("4. Check requirements.txt and install missing packages")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 