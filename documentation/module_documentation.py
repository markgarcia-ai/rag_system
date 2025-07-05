#!/usr/bin/env python3
"""
Module Documentation Generator for RAG System
Generates comprehensive documentation for all modules and creates documentation.html
"""

import os
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
from datetime import datetime
import base64

class DocumentationGenerator:
    def __init__(self, rag_system_path: str = "."):
        self.rag_system_path = Path(rag_system_path)
        self.modules = {}
        self.api_endpoints = []
        self.configuration = {}
        self.markets = {}
        
    def analyze_codebase(self):
        """Analyze the entire RAG system codebase"""
        print("🔍 Analyzing RAG system modules...")
        
        # Core modules to analyze
        core_modules = [
            ("app/financial_agent.py", "Financial Agents"),
            ("app/rag_engine.py", "RAG Engine"),
            ("app/llm_wrapper.py", "LLM Integration"),
            ("app/embedding_model.py", "Embedding Model"),
            ("app/document_loader.py", "Document Loader"),
            ("main.py", "Main Application"),
        ]
        
        for module_path, category in core_modules:
            full_path = self.rag_system_path / module_path
            if full_path.exists():
                self.analyze_module(full_path, module_path, category)
        
        # Analyze data processing
        self.analyze_data_processing()
        
        # Analyze frontend
        self.analyze_frontend()
        
        # Extract API endpoints
        self.extract_api_endpoints()
        
        # Extract configuration
        self.extract_configuration()
        
        # Extract market information
        self.extract_market_info()
    
    def analyze_module(self, file_path: Path, module_name: str, category: str):
        """Analyze a single Python module"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module_info = {
                'name': module_name,
                'category': category,
                'path': str(file_path),
                'classes': [],
                'functions': [],
                'imports': [],
                'docstring': ast.get_docstring(tree) or "",
                'lines_of_code': len(content.split('\n')),
                'description': self.generate_module_description(module_name, category)
            }
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module_info['imports'].append(f"{node.module}.{node.names[0].name}")
                elif isinstance(node, ast.ClassDef):
                    class_info = self.extract_class_info(node)
                    module_info['classes'].append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    func_info = self.extract_function_info(node)
                    module_info['functions'].append(func_info)
            
            self.modules[module_name] = module_info
            
        except Exception as e:
            print(f"⚠️  Error analyzing {module_name}: {e}")
    
    def extract_class_info(self, node: ast.ClassDef) -> Dict:
        """Extract detailed class information"""
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'methods': [self.extract_function_info(item) for item in node.body if isinstance(item, ast.FunctionDef)],
            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'attributes': self.extract_attributes(node)
        }
    
    def extract_function_info(self, node: ast.FunctionDef) -> Dict:
        """Extract detailed function information"""
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'args': [arg.arg for arg in node.args.args],
            'returns': self.extract_return_type(node),
            'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
        }
    
    def extract_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract class attributes"""
        attributes = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        return attributes
    
    def extract_return_type(self, node: ast.FunctionDef) -> str:
        """Extract function return type annotation"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return "Any"
    
    def generate_module_description(self, module_name: str, category: str) -> str:
        """Generate a description for a module based on its name and category"""
        descriptions = {
            "Financial Agents": "Handles financial analysis and investment recommendations through AI agents.",
            "RAG Engine": "Core retrieval-augmented generation pipeline for processing queries and generating responses.",
            "LLM Integration": "Integration layer for the Llama language model for text generation.",
            "Embedding Model": "Manages text embeddings and vector similarity search using SentenceTransformers.",
            "Document Loader": "Handles loading and processing of financial documents and market data.",
            "Main Application": "Flask web server that provides the API endpoints and serves the frontend."
        }
        return descriptions.get(category, f"Module for {category.lower()} functionality.")
    
    def analyze_data_processing(self):
        """Analyze data processing modules"""
        data_modules = [
            ("data/csv_to_text_chunks.py", "Data Processing"),
            ("data/export_crypto_to_csv.py", "Data Export"),
        ]
        
        for module_path, category in data_modules:
            full_path = self.rag_system_path / module_path
            if full_path.exists():
                self.analyze_module(full_path, module_path, category)
    
    def analyze_frontend(self):
        """Analyze frontend files"""
        frontend_files = [
            ("frontend/index.html", "Frontend"),
        ]
        
        for file_path, category in frontend_files:
            full_path = self.rag_system_path / file_path
            if full_path.exists():
                self.analyze_frontend_file(full_path, file_path, category)
    
    def analyze_frontend_file(self, file_path: Path, file_name: str, category: str):
        """Analyze frontend HTML/JS files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_info = {
                'name': file_name,
                'category': category,
                'path': str(file_path),
                'type': 'frontend',
                'description': self.generate_frontend_description(file_name),
                'lines_of_code': len(content.split('\n')),
                'features': self.extract_frontend_features(content)
            }
            
            self.modules[file_name] = module_info
            
        except Exception as e:
            print(f"⚠️  Error analyzing frontend file {file_name}: {e}")
    
    def generate_frontend_description(self, file_name: str) -> str:
        """Generate description for frontend files"""
        if "index.html" in file_name:
            return "Main web interface for the RAG system with chat interface and debug panels."
        return f"Frontend component: {file_name}"
    
    def extract_frontend_features(self, content: str) -> List[str]:
        """Extract features from frontend code"""
        features = []
        if "agent-select" in content:
            features.append("Agent Selection")
        if "market-select" in content:
            features.append("Market Selection")
        if "debug-panel" in content:
            features.append("Debug Information")
        if "chat" in content:
            features.append("Chat Interface")
        return features
    
    def extract_api_endpoints(self):
        """Extract API endpoints from main.py"""
        main_path = self.rag_system_path / "main.py"
        if not main_path.exists():
            return
        
        try:
            with open(main_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and hasattr(node, 'decorator_list'):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr == 'route':
                                endpoint_info = {
                                    'name': node.name,
                                    'route': decorator.args[0].value if decorator.args else '/',
                                    'methods': self.extract_route_methods(decorator),
                                    'docstring': ast.get_docstring(node) or "",
                                    'description': self.generate_endpoint_description(node.name)
                                }
                                self.api_endpoints.append(endpoint_info)
                                
        except Exception as e:
            print(f"⚠️  Error extracting API endpoints: {e}")
    
    def extract_route_methods(self, decorator: ast.Call) -> List[str]:
        """Extract HTTP methods from route decorator"""
        methods = ['GET']  # Default
        for keyword in decorator.keywords:
            if keyword.arg == 'methods':
                if isinstance(keyword.value, ast.List):
                    methods = [elt.value for elt in keyword.value.elts]
        return methods
    
    def generate_endpoint_description(self, endpoint_name: str) -> str:
        """Generate description for API endpoints"""
        descriptions = {
            'chat': 'Process chat queries and return AI-generated responses',
            'chat_debug': 'Process chat queries with detailed debug information',
            'data_info': 'Return information about available market data',
            'root': 'Redirect to the main frontend interface',
            'serve_frontend': 'Serve static frontend files'
        }
        return descriptions.get(endpoint_name, f"API endpoint: {endpoint_name}")
    
    def extract_configuration(self):
        """Extract configuration information"""
        self.configuration = {
            'environment_variables': [
                'COINMARKETCAP_API_KEY',
                'BINANCE_API_KEY',
                'BINANCE_API_SECRET'
            ],
            'model_configuration': {
                'llm_model': 'mistral-7b-instruct-v0.1.Q2_K.gguf',
                'embedding_model': 'all-MiniLM-L6-v2',
                'vector_database': 'ChromaDB',
                'context_length': 2048
            },
            'data_directories': [
                'data/SP500_data',
                'data/NASDAQ_data',
                'data/SP600_data',
                'data/DOWJONES_data',
                'data/NYSE_data',
                'data/CRYPTO_data'
            ],
            'text_directories': [
                'data/SP500_text',
                'data/NASDAQ_text',
                'data/SP600_text',
                'data/DOWJONES_text',
                'data/NYSE_text',
                'data/CRYPTO_text'
            ]
        }
    
    def extract_market_info(self):
        """Extract market information"""
        self.markets = {
            'S&P 500': {
                'description': 'Standard & Poor\'s 500 Index - 500 largest US companies',
                'data_source': 'Yahoo Finance',
                'symbols': '~500 stocks',
                'update_frequency': 'Daily'
            },
            'NASDAQ': {
                'description': 'NASDAQ Composite - Technology-heavy stock market index',
                'data_source': 'Yahoo Finance',
                'symbols': '~3000+ stocks',
                'update_frequency': 'Daily'
            },
            'S&P 600': {
                'description': 'Small-cap stock index of 600 companies',
                'data_source': 'Yahoo Finance',
                'symbols': '~600 stocks',
                'update_frequency': 'Daily'
            },
            'Dow Jones': {
                'description': 'Dow Jones Industrial Average - 30 large US companies',
                'data_source': 'Yahoo Finance',
                'symbols': '30 stocks',
                'update_frequency': 'Daily'
            },
            'NYSE': {
                'description': 'New York Stock Exchange - Major US stock exchange',
                'data_source': 'Yahoo Finance',
                'symbols': '~2000+ stocks',
                'update_frequency': 'Daily'
            },
            'Crypto': {
                'description': 'Major cryptocurrencies including BTC, ETH, BNB, etc.',
                'data_source': 'Yahoo Finance',
                'symbols': '20 main coins',
                'update_frequency': 'Daily'
            }
        }
    
    def get_diagram_base64(self, diagram_path: str) -> str:
        """Convert PNG diagram to base64 for embedding in HTML"""
        try:
            diagram_file = self.rag_system_path / "documentation" / diagram_path
            if diagram_file.exists():
                with open(diagram_file, 'rb') as f:
                    image_data = f.read()
                    return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"⚠️  Error loading diagram {diagram_path}: {e}")
        return ""
    
    def generate_detailed_rag_diagram(self) -> str:
        """Generate a detailed RAG system diagram showing agents and retrieval"""
        print("🎨 Generating detailed RAG system diagram...")
        
        plantuml = """
@startuml RAG_System_Detailed_Architecture
!theme plain
title RAG System - Detailed Architecture with Agents and Retrieval

skinparam componentStyle rectangle

package "User Interface" {
    [Web Browser] as UI
    [Agent Selector] as AS
    [Market Selector] as MS
    [Query Input] as QI
    [Debug Panel] as DP
}

package "Flask Backend" {
    [Flask Server] as FS
    [API Router] as AR
    [Request Handler] as RH
}

package "Agent Layer" {
    [Financial RAG Agent] as FRA
    [Broker Agent] as BA
    [Agent Factory] as AF
}

package "RAG Pipeline" {
    [Query Processor] as QP
    [Embedding Generator] as EG
    [Vector Search] as VS
    [Document Retriever] as DR
    [Context Builder] as CB
    [Prompt Constructor] as PC
}

package "LLM Layer" {
    [Llama Model] as LLM
    [Response Generator] as RG
    [Token Counter] as TC
}

package "Data Layer" {
    [ChromaDB] as CDB
    [Vector Store] as VS
    [Document Store] as DS
}

package "Document Processing" {
    [CSV Loader] as CL
    [Text Chunker] as TC
    [Embedding Model] as EM
    [Financial Concepts] as FC
}

package "Market Data" {
    [S&P 500 Data] as SP500
    [NASDAQ Data] as NASDAQ
    [Crypto Data] as CRYPTO
    [Other Markets] as OTHER
}

' User Interface Flow
UI --> AS
UI --> MS
UI --> QI
UI --> DP

' Backend Flow
AS --> FS
MS --> FS
QI --> FS
FS --> AR
AR --> RH

' Agent Selection
RH --> AF
AF --> FRA
AF --> BA

' RAG Pipeline Flow
FRA --> QP
BA --> QP
QP --> EG
EG --> VS
VS --> CDB
CDB --> DR
DR --> CB
CB --> PC
PC --> LLM
LLM --> RG
RG --> TC
TC --> RH
RH --> UI

' Data Flow
SP500 --> CL
NASDAQ --> CL
CRYPTO --> CL
OTHER --> CL
CL --> TC
TC --> EM
EM --> VS
FC --> VS

' Debug Information
QP --> DP
EG --> DP
VS --> DP
DR --> DP
CB --> DP
PC --> DP
RG --> DP
TC --> DP

' Market Data Access
BA --> SP500
BA --> NASDAQ
BA --> CRYPTO
BA --> OTHER

@enduml
"""
        return plantuml
    
    def generate_agent_interaction_diagram(self) -> str:
        """Generate diagram showing agent interactions and decision flow"""
        print("🤖 Generating agent interaction diagram...")
        
        plantuml = """
@startuml RAG_Agent_Interactions
!theme plain
title RAG System - Agent Interactions and Decision Flow

actor User
participant "Frontend" as UI
participant "Flask API" as API
participant "Agent Selector" as AS
participant "Financial RAG Agent" as FRA
participant "Broker Agent" as BA
participant "RAG Engine" as RAG
participant "Market Data" as MD
participant "Vector DB" as VDB
participant "LLM" as LLM

User -> UI: Select Agent & Market
User -> UI: Enter Query
UI -> API: POST /chat_debug

alt Financial RAG Agent Selected
    API -> AS: Route to FRA
    AS -> FRA: Process Query
    FRA -> RAG: query_rag_debug()
    RAG -> VDB: Search Documents
    VDB -> RAG: Retrieved Docs
    RAG -> LLM: Generate Response
    LLM -> RAG: Response Text
    RAG -> FRA: Debug Info
    FRA -> API: Return Response
else Broker Agent Selected
    API -> AS: Route to BA
    AS -> BA: Process Query
    BA -> MD: Analyze Market Data
    MD -> BA: Market Statistics
    BA -> BA: Calculate Best Stock
    BA -> API: Return Recommendation
end

API -> UI: JSON Response
UI -> User: Display Answer & Debug Info

@enduml
"""
        return plantuml
    
    def generate_documentation_html(self) -> str:
        """Generate comprehensive documentation HTML"""
        print("📝 Generating documentation.html...")
        
        # Get base64 encoded diagrams
        class_diagram_b64 = self.get_diagram_base64("class_diagram.png")
        component_diagram_b64 = self.get_diagram_base64("component_diagram.png")
        sequence_diagram_b64 = self.get_diagram_base64("sequence_diagram.png")
        tech_stack_b64 = self.get_diagram_base64("technology_stack.png")
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG System Documentation</title>
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
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
        }}
        .module-card {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .module-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .module-name {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }}
        .module-category {{
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
        }}
        .code-block {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }}
        .endpoint {{
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .method {{
            background: #4caf50;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-right: 10px;
        }}
        .market-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .market-card {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
        }}
        .toc {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 8px 0;
        }}
        .toc a {{
            color: #3498db;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2196f3;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .diagram-section {{
            margin: 30px 0;
            text-align: center;
        }}
        .diagram-container {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .diagram-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .diagram-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 RAG System Documentation</h1>
        <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        
        <div class="toc">
            <h2>📋 Table of Contents</h2>
            <ul>
                <li><a href="#overview">System Overview</a></li>
                <li><a href="#architecture">Architecture</a></li>
                <li><a href="#diagrams">System Diagrams</a></li>
                <li><a href="#modules">Modules</a></li>
                <li><a href="#api">API Endpoints</a></li>
                <li><a href="#configuration">Configuration</a></li>
                <li><a href="#markets">Supported Markets</a></li>
                <li><a href="#usage">Usage Guide</a></li>
            </ul>
        </div>

        <section id="overview">
            <h2>🎯 System Overview</h2>
            <p>The RAG (Retrieval-Augmented Generation) System is a comprehensive financial analysis platform that combines:</p>
            <ul>
                <li><strong>Multi-market data</strong>: S&P 500, NASDAQ, S&P 600, Dow Jones, NYSE, and Crypto markets</li>
                <li><strong>AI agents</strong>: Financial RAG Agent and Broker Agent for different types of analysis</li>
                <li><strong>Vector search</strong>: Semantic search through financial documents and market data</li>
                <li><strong>LLM integration</strong>: Local Llama model for generating responses</li>
                <li><strong>Web interface</strong>: Interactive chat interface with debug information</li>
            </ul>
        </section>

        <section id="architecture">
            <h2>🏗️ Architecture</h2>
            <p>The system follows a modular architecture with clear separation of concerns:</p>
            <div class="code-block">
Frontend (HTML/JS) → Flask API → Agent Layer → RAG Engine → Embedding Model → ChromaDB
                                 ↓
                            LLM (Llama) → Response Generation
            </div>
        </section>

        <section id="diagrams">
            <h2>📊 System Diagrams</h2>
            
            <div class="diagram-section">
                <div class="diagram-container">
                    <div class="diagram-title">🏗️ System Architecture (Component Diagram)</div>
                    <img src="data:image/png;base64,{component_diagram_b64}" alt="Component Diagram">
                </div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-container">
                    <div class="diagram-title">🔄 Query Processing Flow (Sequence Diagram)</div>
                    <img src="data:image/png;base64,{sequence_diagram_b64}" alt="Sequence Diagram">
                </div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-container">
                    <div class="diagram-title">📈 Data Flow Architecture</div>
                    <img src="data:image/png;base64,{class_diagram_b64}" alt="Class Diagram">
                </div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-container">
                    <div class="diagram-title">🛠️ Technology Stack</div>
                    <img src="data:image/png;base64,{tech_stack_b64}" alt="Technology Stack">
                </div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-container">
                    <div class="diagram-title">🤖 Agent Interaction Flow</div>
                    <div class="code-block">
{self.generate_agent_interaction_diagram()}
                    </div>
                    <p><em>This diagram shows how different agents interact with the RAG system and make decisions.</em></p>
                </div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-container">
                    <div class="diagram-title">🎯 Detailed RAG Architecture with Agents</div>
                    <div class="code-block">
{self.generate_detailed_rag_diagram()}
                    </div>
                    <p><em>This diagram shows the complete RAG system architecture including agent linkages and retrieval processes.</em></p>
                </div>
            </div>
        </section>

        <section id="modules">
            <h2>📦 Modules</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(self.modules)}</div>
                    <div class="stat-label">Total Modules</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(self.api_endpoints)}</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(self.markets)}</div>
                    <div class="stat-label">Supported Markets</div>
                </div>
            </div>
"""
        
        # Add module documentation
        for module_name, module_info in self.modules.items():
            html += f"""
            <div class="module-card">
                <div class="module-header">
                    <div class="module-name">{module_name}</div>
                    <div class="module-category">{module_info['category']}</div>
                </div>
                <p><strong>Description:</strong> {module_info['description']}</p>
                <p><strong>Path:</strong> <code>{module_info['path']}</code></p>
                <p><strong>Lines of Code:</strong> {module_info['lines_of_code']}</p>
"""
            
            if module_info.get('classes'):
                html += "<p><strong>Classes:</strong></p><ul>"
                for class_info in module_info['classes']:
                    html += f"<li><code>{class_info['name']}</code> - {class_info['docstring'][:100]}...</li>"
                html += "</ul>"
            
            if module_info.get('functions'):
                html += "<p><strong>Functions:</strong></p><ul>"
                for func_info in module_info['functions'][:5]:  # Limit to first 5
                    html += f"<li><code>{func_info['name']}()</code> - {func_info['docstring'][:80]}...</li>"
                html += "</ul>"
            
            html += "</div>"
        
        # Add API endpoints
        html += """
        <section id="api">
            <h2>🔌 API Endpoints</h2>
        """
        
        for endpoint in self.api_endpoints:
            methods_str = ', '.join(endpoint['methods'])
            html += f"""
            <div class="endpoint">
                <h3><span class="method">{methods_str}</span> {endpoint['route']}</h3>
                <p><strong>Function:</strong> <code>{endpoint['name']}</code></p>
                <p><strong>Description:</strong> {endpoint['description']}</p>
                <p><strong>Documentation:</strong> {endpoint['docstring']}</p>
            </div>
            """
        
        # Add configuration
        html += """
        <section id="configuration">
            <h2>⚙️ Configuration</h2>
            <h3>Environment Variables</h3>
            <ul>
        """
        
        for env_var in self.configuration['environment_variables']:
            html += f"<li><code>{env_var}</code></li>"
        
        html += """
            </ul>
            <h3>Model Configuration</h3>
        """
        
        for key, value in self.configuration['model_configuration'].items():
            html += f"<p><strong>{key}:</strong> <code>{value}</code></p>"
        
        # Add markets
        html += """
        <section id="markets">
            <h2>📊 Supported Markets</h2>
            <div class="market-info">
        """
        
        for market_name, market_info in self.markets.items():
            html += f"""
            <div class="market-card">
                <h3>{market_name}</h3>
                <p><strong>Description:</strong> {market_info['description']}</p>
                <p><strong>Data Source:</strong> {market_info['data_source']}</p>
                <p><strong>Symbols:</strong> {market_info['symbols']}</p>
                <p><strong>Update Frequency:</strong> {market_info['update_frequency']}</p>
            </div>
            """
        
        html += """
            </div>
        </section>

        <section id="usage">
            <h2>📖 Usage Guide</h2>
            <h3>Getting Started</h3>
            <ol>
                <li><strong>Install Dependencies:</strong> <code>pip install -r requirements.txt</code></li>
                <li><strong>Activate Virtual Environment:</strong> <code>source venv/bin/activate</code></li>
                <li><strong>Download Data:</strong> Run data download scripts for desired markets</li>
                <li><strong>Process Data:</strong> Run <code>csv_to_text_chunks.py</code> to create text chunks</li>
                <li><strong>Start Backend:</strong> <code>python main.py</code></li>
                <li><strong>Access Frontend:</strong> Open browser to <code>http://localhost:5000</code></li>
            </ol>
            
            <h3>Agent Selection</h3>
            <ul>
                <li><strong>Financial RAG Agent:</strong> Use for general financial questions, market analysis, and concept explanations</li>
                <li><strong>Broker Agent:</strong> Use for investment recommendations, portfolio advice, and stock selection</li>
            </ul>
            
            <h3>Market Selection</h3>
            <ul>
                <li><strong>S&P 500:</strong> Large-cap US stocks (500 companies)</li>
                <li><strong>NASDAQ:</strong> Technology-heavy stocks (3000+ companies)</li>
                <li><strong>S&P 600:</strong> Small-cap stocks (600 companies)</li>
                <li><strong>Dow Jones:</strong> 30 large US companies</li>
                <li><strong>NYSE:</strong> New York Stock Exchange (2000+ companies)</li>
                <li><strong>Crypto:</strong> Major cryptocurrencies (20 coins)</li>
            </ul>
            
            <h3>Example Queries</h3>
            <ul>
                <li>"What is the P/E ratio?" (Financial RAG Agent)</li>
                <li>"How did AAPL perform in June 2024?" (Financial RAG Agent)</li>
                <li>"What is the best stock to invest in right now?" (Broker Agent)</li>
                <li>"Explain the difference between value and growth investing." (Financial RAG Agent)</li>
                <li>"Recommend a diversified portfolio for a moderate risk investor." (Broker Agent)</li>
            </ul>
        </section>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_documentation(self, output_dir: str = "documentation"):
        """Save documentation files"""
        output_path = self.rag_system_path / output_dir
        output_path.mkdir(exist_ok=True)
        
        # Generate and save HTML documentation
        html_content = self.generate_documentation_html()
        html_file = output_path / 'documentation.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Saved documentation.html")
        
        # Save module analysis as JSON
        analysis_data = {
            'modules': self.modules,
            'api_endpoints': self.api_endpoints,
            'configuration': self.configuration,
            'markets': self.markets,
            'generated_at': datetime.now().isoformat()
        }
        
        json_file = output_path / 'module_analysis.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
        print(f"✅ Saved module_analysis.json")
        
        print(f"\n🎉 Documentation generated successfully!")
        print(f"📄 View documentation at: {html_file}")
        return output_path

def main():
    """Main function to generate documentation"""
    print("🚀 Starting Module Documentation Generation for RAG System")
    print("=" * 60)
    
    generator = DocumentationGenerator()
    generator.analyze_codebase()
    output_path = generator.save_documentation()
    
    print("\n📋 Generated Files:")
    for file in output_path.glob("*"):
        print(f"  - {file.name}")
    
    print("\n💡 Next Steps:")
    print("  1. Open documentation.html in your browser")
    print("  2. Review the comprehensive system documentation")
    print("  3. Use module_analysis.json for programmatic access")

if __name__ == "__main__":
    main() 