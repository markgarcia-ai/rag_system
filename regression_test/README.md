# RAG System Regression Testing

This directory contains comprehensive regression tests for the RAG (Retrieval-Augmented Generation) system.

## Overview

The regression testing system validates all critical components of the RAG system:

- ✅ **Module Imports** - Ensures all required modules can be imported
- ✅ **Vector Database** - Tests ChromaDB connectivity and collections
- ✅ **Embedding Model** - Validates sentence transformer functionality
- ✅ **LLM Model** - Tests Llama model responses
- ✅ **Document Retrieval** - Verifies RAG pipeline functionality
- ✅ **Market Data Availability** - Checks if market data is accessible
- ✅ **Financial RAG Agent** - Tests the main financial analysis agent
- ✅ **Broker Agent** - Validates investment recommendation agent
- ✅ **Stock Agent** - Tests prompt engineering and JSON output

## Quick Start

### 1. Run Tests
```bash
cd rag_system/regression_test
python run_tests.py
```

### 2. View Results
After running tests, open `regression_test_report.html` in your browser to see detailed results.

## Test Components

### Core System Tests
- **Module Imports**: Validates all Python dependencies
- **Vector Database**: Tests ChromaDB connection and data access
- **Embedding Model**: Verifies sentence transformer functionality
- **LLM Model**: Tests Llama model responses

### Agent Tests
- **Financial RAG Agent**: Tests main financial analysis capabilities
- **Broker Agent**: Validates investment recommendations
- **Stock Agent**: Tests prompt engineering and JSON decision output

### Data Tests
- **Market Data**: Verifies availability of market data
- **Document Retrieval**: Tests the complete RAG pipeline

## HTML Report Features

The generated HTML report includes:

- 📊 **Summary Dashboard** with pass/fail statistics
- ⏱️ **Performance Metrics** with test durations
- 🔍 **Detailed Results** for each test component
- 📝 **Error Details** for failed tests
- 🕒 **Timestamps** for all test runs

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the virtual environment
   ```bash
   source venv/bin/activate
   ```

2. **Model Loading Errors**: Ensure the Llama model file exists
   ```bash
   ls models/mistral-7b-instruct-v0.1.Q2_K.gguf
   ```

3. **Vector Database Errors**: Check if ChromaDB data exists
   ```bash
   ls vectorstore/
   ```

4. **Market Data Errors**: Verify data files are present
   ```bash
   ls data/*_data/
   ```

### Running Individual Tests

You can modify `test_runner.py` to run specific tests by commenting out unwanted test functions.

## Configuration

### Test Timeouts
- Default timeout: 5 minutes for all tests
- Individual test timeout: 30 seconds

### Output Location
- HTML Report: `regression_test_report.html`
- Logs: Printed to console

## Dependencies

Install test dependencies:
```bash
pip install -r requirements.txt
```

## Continuous Integration

The regression tests can be integrated into CI/CD pipelines:

```bash
cd rag_system/regression_test
python run_tests.py
# Exit code 0 = all tests passed, 1 = some tests failed
```

## Contributing

To add new tests:

1. Add a new test method to `RegressionTestRunner`
2. Include it in the `run_all_tests()` method
3. Update this README with test description
4. Test thoroughly before committing 