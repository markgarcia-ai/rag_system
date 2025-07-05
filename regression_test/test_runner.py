#!/usr/bin/env python3
"""
Regression Test Runner for RAG System
Tests all components and generates HTML report
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import subprocess

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class RegressionTestRunner:
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log a test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
            if details:
                print(f"   Details: {details}")
        
        self.total_tests += 1
    
    def test_imports(self) -> bool:
        """Test if all required modules can be imported"""
        test_name = "Module Imports"
        start_time = time.time()
        
        try:
            # Test core imports
            from app.rag_engine import query_rag
            from app.embedding_model import query_embedding
            from app.llm_wrapper import query_llm
            from app.financial_agent import FinancialRAGAgent, BrokerAgent
            
            # Test agent imports
            from agent.stock_agent import StockAgent
            
            duration = time.time() - start_time
            self.log_test(test_name, "PASS", "All modules imported successfully", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Import error: {str(e)}", duration)
            return False
    
    def test_embedding_model(self) -> bool:
        """Test embedding model functionality"""
        test_name = "Embedding Model"
        start_time = time.time()
        
        try:
            from app.embedding_model import query_embedding
            
            # Test embedding generation
            test_text = "This is a test query for embedding"
            embedding = query_embedding(test_text)
            
            if embedding is not None and len(embedding) > 0:
                duration = time.time() - start_time
                self.log_test(test_name, "PASS", f"Generated embedding with {len(embedding)} dimensions", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "Embedding generation returned None or empty", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Embedding error: {str(e)}", duration)
            return False
    
    def test_llm_model(self) -> bool:
        """Test LLM model functionality"""
        test_name = "LLM Model"
        start_time = time.time()
        
        try:
            from app.llm_wrapper import query_llm
            
            # Test simple LLM query
            test_prompt = "What is 2+2? Answer with just the number."
            response = query_llm(test_prompt)
            
            if response and len(response.strip()) > 0:
                duration = time.time() - start_time
                self.log_test(test_name, "PASS", f"LLM response: {response[:50]}...", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "LLM returned empty response", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"LLM error: {str(e)}", duration)
            return False
    
    def test_retrieval_system(self) -> bool:
        """Test document retrieval functionality"""
        test_name = "Document Retrieval"
        start_time = time.time()
        
        try:
            from app.rag_engine import query_rag
            
            # Test retrieval with a simple query
            test_query = "What is a stock?"
            response = query_rag(test_query)
            
            if response and len(response.strip()) > 0:
                duration = time.time() - start_time
                self.log_test(test_name, "PASS", f"Retrieval response: {response[:100]}...", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "Retrieval returned empty response", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Retrieval error: {str(e)}", duration)
            return False
    
    def test_financial_rag_agent(self) -> bool:
        """Test Financial RAG Agent"""
        test_name = "Financial RAG Agent"
        start_time = time.time()
        
        try:
            from app.financial_agent import FinancialRAGAgent
            
            agent = FinancialRAGAgent()
            test_query = "What is the P/E ratio?"
            result = agent.answer(test_query, market="S&P 500")
            
            if result and 'answer' in result:
                duration = time.time() - start_time
                self.log_test(test_name, "PASS", f"Agent response: {result['answer'][:100]}...", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "Agent returned invalid response format", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Agent error: {str(e)}", duration)
            return False
    
    def test_broker_agent(self) -> bool:
        """Test Broker Agent"""
        test_name = "Broker Agent"
        start_time = time.time()
        
        try:
            from app.financial_agent import BrokerAgent
            
            agent = BrokerAgent()
            test_query = "What is the best stock to invest in?"
            result = agent.answer(test_query, market="S&P 500")
            
            if result and 'answer' in result:
                duration = time.time() - start_time
                self.log_test(test_name, "PASS", f"Broker response: {result['answer'][:100]}...", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "Broker agent returned invalid response format", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Broker agent error: {str(e)}", duration)
            return False
    
    def test_stock_agent(self) -> bool:
        """Test Stock Agent with prompt engineering"""
        test_name = "Stock Agent (Prompt Engineering)"
        start_time = time.time()
        
        try:
            from agent.stock_agent import StockAgent
            
            agent = StockAgent()
            test_query = "Should I buy AAPL?"
            decision = agent.get_decision(test_query, market="NASDAQ")
            
            if decision and isinstance(decision, dict):
                duration = time.time() - start_time
                self.log_test(test_name, "PASS", f"Stock agent decision: {json.dumps(decision, indent=2)}", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "Stock agent returned invalid decision format", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Stock agent error: {str(e)}", duration)
            return False
    
    def test_data_availability(self) -> bool:
        """Test if market data is available"""
        test_name = "Market Data Availability"
        start_time = time.time()
        
        try:
            from app.financial_agent import get_data_info
            
            data_info = get_data_info()
            
            if data_info and 'markets' in data_info and len(data_info['markets']) > 0:
                duration = time.time() - start_time
                markets = [m['market'] for m in data_info['markets']]
                self.log_test(test_name, "PASS", f"Available markets: {', '.join(markets)}", duration)
                return True
            else:
                duration = time.time() - start_time
                self.log_test(test_name, "FAIL", "No market data available", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Data availability error: {str(e)}", duration)
            return False
    
    def test_vector_database(self) -> bool:
        """Test vector database connectivity"""
        test_name = "Vector Database"
        start_time = time.time()
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Try to connect to ChromaDB
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./vectorstore"
            ))
            
            # Check if collections exist
            collections = client.list_collections()
            
            duration = time.time() - start_time
            self.log_test(test_name, "PASS", f"Connected to ChromaDB. Collections: {len(collections)}", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Vector database error: {str(e)}", duration)
            return False
    
    def generate_html_report(self) -> str:
        """Generate HTML report with test results"""
        total_duration = time.time() - self.start_time
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG System Regression Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .summary-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .total {{ color: #007bff; }}
        .duration {{ color: #6c757d; }}
        .test-results {{
            margin-top: 30px;
        }}
        .test-item {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .test-name {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .test-status {{
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .test-details {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
            margin-top: 10px;
            white-space: pre-wrap;
        }}
        .test-duration {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 0.8em;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 RAG System Regression Test Report</h1>
        <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        
        <div class="summary">
            <div class="summary-card">
                <div class="summary-number total">{self.total_tests}</div>
                <div>Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="summary-number passed">{self.passed_tests}</div>
                <div>Passed</div>
            </div>
            <div class="summary-card">
                <div class="summary-number failed">{self.failed_tests}</div>
                <div>Failed</div>
            </div>
            <div class="summary-card">
                <div class="summary-number duration">{success_rate:.1f}%</div>
                <div>Success Rate</div>
            </div>
            <div class="summary-card">
                <div class="summary-number duration">{total_duration:.2f}s</div>
                <div>Total Duration</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>📋 Test Results</h2>
"""
        
        for result in self.test_results:
            status_class = "status-pass" if result["status"] == "PASS" else "status-fail"
            html += f"""
            <div class="test-item">
                <div class="test-header">
                    <div class="test-name">{result["test_name"]}</div>
                    <div class="test-status {status_class}">{result["status"]}</div>
                </div>
                <div class="test-duration">Duration: {result["duration"]:.2f}s</div>
                <div class="timestamp">Timestamp: {result["timestamp"]}</div>
"""
            
            if result["details"]:
                html += f'<div class="test-details">{result["details"]}</div>'
            
            html += "</div>"
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all regression tests"""
        print("🚀 Starting RAG System Regression Tests")
        print("=" * 60)
        
        # Run tests in logical order
        tests = [
            ("Module Imports", self.test_imports),
            ("Vector Database", self.test_vector_database),
            ("Embedding Model", self.test_embedding_model),
            ("LLM Model", self.test_llm_model),
            ("Document Retrieval", self.test_retrieval_system),
            ("Market Data Availability", self.test_data_availability),
            ("Financial RAG Agent", self.test_financial_rag_agent),
            ("Broker Agent", self.test_broker_agent),
            ("Stock Agent (Prompt Engineering)", self.test_stock_agent),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Unexpected error: {str(e)}\n{traceback.format_exc()}", 0)
        
        # Generate report
        total_duration = time.time() - self.start_time
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "results": self.test_results
        }

def main():
    """Main function to run regression tests"""
    runner = RegressionTestRunner()
    results = runner.run_all_tests()
    
    # Generate and save HTML report
    html_report = runner.generate_html_report()
    report_path = Path(__file__).parent / "regression_test_report.html"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"\n📄 HTML Report generated: {report_path}")
    print(f"🌐 Open the report in your browser to view detailed results")
    
    # Return exit code based on test results
    return 0 if results["failed_tests"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 