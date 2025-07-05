#!/usr/bin/env python3
"""
Simple script to run regression tests
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run regression tests"""
    print("🧪 RAG System Regression Testing")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("test_runner.py").exists():
        print("❌ Error: test_runner.py not found. Make sure you're in the regression_test directory.")
        return 1
    
    try:
        # Run the test runner
        result = subprocess.run([sys.executable, "test_runner.py"], 
                              capture_output=True, text=True, timeout=300)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Check if HTML report was generated
        report_path = Path("regression_test_report.html")
        if report_path.exists():
            print(f"\n✅ HTML Report generated: {report_path.absolute()}")
            print("🌐 Open the report in your browser to view detailed results")
        else:
            print("❌ HTML report was not generated")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 