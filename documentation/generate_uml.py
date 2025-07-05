#!/usr/bin/env python3
"""
UML Diagram Generator for RAG System
Generates various UML diagrams to visualize the system architecture
"""

import os
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import subprocess
import sys

class UMLGenerator:
    def __init__(self, rag_system_path: str = "."):
        self.rag_system_path = Path(rag_system_path)
        self.classes = {}
        self.functions = {}
        self.modules = {}
        self.relationships = []
        
    def check_plantuml_installation(self) -> bool:
        """Check if PlantUML is installed and available"""
        try:
            result = subprocess.run(['plantuml', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def install_plantuml_python(self):
        """Install plantuml Python package if not available"""
        try:
            import plantuml
            return True
        except ImportError:
            print("📦 Installing plantuml Python package...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'plantuml'])
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install plantuml package")
                return False
    
    def generate_png_from_plantuml(self, puml_file: Path) -> bool:
        """Generate PNG from PlantUML file"""
        try:
            # Try using plantuml Python package first
            import plantuml
            server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
            
            with open(puml_file, 'r', encoding='utf-8') as f:
                puml_content = f.read()
            
            png_file = puml_file.with_suffix('.png')
            server.processes_file(str(puml_file), outfile=str(png_file))
            return True
            
        except Exception as e:
            print(f"⚠️  Python plantuml failed: {e}")
            
            # Fallback to command line plantuml
            try:
                result = subprocess.run(['plantuml', '-tpng', str(puml_file)], 
                                      capture_output=True, text=True, timeout=30)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"❌ Command line plantuml failed: {e}")
                return False
    
    def analyze_codebase(self):
        """Analyze the entire RAG system codebase"""
        print("🔍 Analyzing RAG system codebase...")
        
        # Analyze main modules
        modules_to_analyze = [
            "app/financial_agent.py",
            "app/rag_engine.py", 
            "app/llm_wrapper.py",
            "app/embedding_model.py",
            "app/document_loader.py",
            "main.py"
        ]
        
        for module_path in modules_to_analyze:
            full_path = self.rag_system_path / module_path
            if full_path.exists():
                self.analyze_module(full_path, module_path)
        
        # Analyze crypto bot if available
        crypto_bot_path = self.rag_system_path.parent / "cyrpto_bot"
        if crypto_bot_path.exists():
            self.analyze_crypto_bot(crypto_bot_path)
    
    def analyze_module(self, file_path: Path, module_name: str):
        """Analyze a single Python module"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.extract_class_info(node, module_name)
                elif isinstance(node, ast.FunctionDef):
                    self.extract_function_info(node, module_name)
                    
        except Exception as e:
            print(f"⚠️  Error analyzing {module_name}: {e}")
    
    def analyze_crypto_bot(self, crypto_bot_path: Path):
        """Analyze crypto bot modules for integration"""
        crypto_modules = [
            "src/data/coin_database.py",
            "src/data/data_fetcher.py"
        ]
        
        for module_path in crypto_modules:
            full_path = crypto_bot_path / module_path
            if full_path.exists():
                self.analyze_module(full_path, f"crypto_bot/{module_path}")
    
    def extract_class_info(self, node: ast.ClassDef, module_name: str):
        """Extract class information from AST node"""
        class_info = {
            'name': node.name,
            'module': module_name,
            'methods': [],
            'attributes': [],
            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'docstring': ast.get_docstring(node) or ""
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append({
                    'name': item.name,
                    'docstring': ast.get_docstring(item) or ""
                })
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['attributes'].append(target.id)
        
        self.classes[f"{module_name}.{node.name}"] = class_info
    
    def extract_function_info(self, node: ast.FunctionDef, module_name: str):
        """Extract function information from AST node"""
        func_info = {
            'name': node.name,
            'module': module_name,
            'docstring': ast.get_docstring(node) or "",
            'args': [arg.arg for arg in node.args.args]
        }
        
        self.functions[f"{module_name}.{node.name}"] = func_info
    
    def generate_class_diagram(self) -> str:
        """Generate PlantUML class diagram"""
        print("📊 Generating class diagram...")
        
        plantuml = """
@startuml RAG_System_Class_Diagram
!theme plain
title RAG System - Class Diagram

"""
        
        # Add classes
        for class_name, class_info in self.classes.items():
            plantuml += f'class "{class_info["name"]}" {{\n'
            
            # Add attributes
            for attr in class_info['attributes'][:5]:  # Limit to first 5
                plantuml += f'  {attr}\n'
            
            # Add methods
            for method in class_info['methods'][:5]:  # Limit to first 5
                plantuml += f'  {method["name"]}()\n'
            
            plantuml += '}\n\n'
        
        # Add relationships
        for class_name, class_info in self.classes.items():
            for base in class_info['bases']:
                plantuml += f'"{base}" <|-- "{class_info["name"]}"\n'
        
        plantuml += "\n@enduml"
        return plantuml
    
    def generate_component_diagram(self) -> str:
        """Generate PlantUML component diagram"""
        print("🔧 Generating component diagram...")
        
        plantuml = """
@startuml RAG_System_Component_Diagram
!theme plain
title RAG System - Component Diagram

package "Frontend" {
    [Web Interface] as UI
    [Market Selector] as MS
    [Agent Selector] as AS
}

package "Backend API" {
    [Flask Server] as API
    [Chat Endpoint] as CE
    [Data Info Endpoint] as DIE
}

package "RAG Pipeline" {
    [Query Processing] as QP
    [Embedding Model] as EM
    [Vector Database] as VD
    [Document Retrieval] as DR
    [LLM Generation] as LG
}

package "Data Layer" {
    [Market Data] as MD
    [Text Chunks] as TC
    [Financial Concepts] as FC
}

package "Agents" {
    [Financial RAG Agent] as FRA
    [Broker Agent] as BA
}

' Frontend to Backend
UI --> API
MS --> API
AS --> API

' API to RAG Pipeline
API --> QP
CE --> QP
DIE --> MD

' RAG Pipeline Flow
QP --> EM
EM --> VD
VD --> DR
DR --> LG

' Data Sources
MD --> TC
TC --> VD
FC --> VD

' Agents
FRA --> QP
BA --> MD

@enduml
"""
        return plantuml
    
    def generate_sequence_diagram(self) -> str:
        """Generate PlantUML sequence diagram"""
        print("🔄 Generating sequence diagram...")
        
        plantuml = """
@startuml RAG_System_Sequence_Diagram
!theme plain
title RAG System - Query Processing Sequence

actor User
participant "Frontend" as UI
participant "Flask API" as API
participant "RAG Engine" as RAG
participant "Embedding Model" as EM
participant "ChromaDB" as DB
participant "LLM" as LLM

User -> UI: Ask Question
UI -> API: POST /chat_debug
API -> RAG: query_rag_debug()
RAG -> EM: query_embedding()
EM -> DB: similarity_search()
DB -> EM: top_k_documents
EM -> RAG: retrieved_docs
RAG -> LLM: generate_answer()
LLM -> RAG: response_text
RAG -> API: debug_info
API -> UI: JSON response
UI -> User: Display Answer

@enduml
"""
        return plantuml
    
    def generate_data_flow_diagram(self) -> str:
        """Generate PlantUML data flow diagram"""
        print("📈 Generating data flow diagram...")
        
        plantuml = """
@startuml RAG_System_Data_Flow
!theme plain
title RAG System - Data Flow Diagram

!define RECTANGLE class

RECTANGLE "CSV Files\n(SP500, NASDAQ, Crypto)" as CSV
RECTANGLE "Text Chunks\n(Processed Data)" as TC
RECTANGLE "Embeddings\n(Vector Representations)" as EMB
RECTANGLE "ChromaDB\n(Vector Store)" as DB
RECTANGLE "User Query" as Q
RECTANGLE "Retrieved Documents" as RD
RECTANGLE "LLM Response" as RESP

CSV --> TC : csv_to_text_chunks.py
TC --> EMB : sentence_transformers
EMB --> DB : persist_embeddings()
Q --> EMB : query_embedding()
EMB --> DB : similarity_search()
DB --> RD : top_k_results
RD --> RESP : generate_answer()

@enduml
"""
        return plantuml
    
    def generate_technology_stack(self) -> str:
        """Generate technology stack diagram"""
        print("🛠️  Generating technology stack diagram...")
        
        plantuml = """
@startuml RAG_System_Technology_Stack
!theme plain
title RAG System - Technology Stack

package "Frontend" {
    [HTML/CSS/JavaScript] as FE
}

package "Backend" {
    [Flask] as FLASK
    [Python 3.11] as PYTHON
}

package "AI/ML" {
    [SentenceTransformers] as ST
    [Llama.cpp] as LLAMA
    [ChromaDB] as CHROMA
}

package "Data Processing" {
    [Pandas] as PD
    [yfinance] as YF
    [CSV Processing] as CSV
}

package "Deployment" {
    [Virtual Environment] as VENV
    [Local Development] as LOCAL
}

FE --> FLASK
FLASK --> PYTHON
PYTHON --> ST
PYTHON --> LLAMA
PYTHON --> CHROMA
PYTHON --> PD
PYTHON --> YF
PYTHON --> CSV
PYTHON --> VENV
VENV --> LOCAL

@enduml
"""
        return plantuml
    
    def generate_mermaid_diagrams(self) -> Dict[str, str]:
        """Generate Mermaid diagrams for web display"""
        print("🌊 Generating Mermaid diagrams...")
        
        mermaid_diagrams = {}
        
        # Class diagram in Mermaid
        mermaid_diagrams['class_diagram'] = """
```mermaid
classDiagram
    class FinancialRAGAgent {
        +name: str
        +description: str
        +answer(question, market)
    }
    
    class BrokerAgent {
        +name: str
        +description: str
        +answer(question, market)
    }
    
    class DataFetcher {
        +mode: str
        +get_top_coins()
        +get_historical_data()
    }
    
    class CoinDatabase {
        +db_path: str
        +update_coin_data()
        +get_all_coins()
    }
    
    FinancialRAGAgent --> DataFetcher
    BrokerAgent --> CoinDatabase
```
"""
        
        # Component diagram in Mermaid
        mermaid_diagrams['component_diagram'] = """
```mermaid
graph TB
    subgraph Frontend
        UI[Web Interface]
        MS[Market Selector]
        AS[Agent Selector]
    end
    
    subgraph Backend
        API[Flask API]
        RAG[RAG Engine]
        EM[Embedding Model]
        DB[ChromaDB]
        LLM[Llama Model]
    end
    
    subgraph Data
        CSV[CSV Files]
        TC[Text Chunks]
        FC[Financial Concepts]
    end
    
    UI --> API
    MS --> API
    AS --> API
    API --> RAG
    RAG --> EM
    EM --> DB
    RAG --> LLM
    CSV --> TC
    TC --> DB
    FC --> DB
```
"""
        
        return mermaid_diagrams
    
    def save_diagrams(self, output_dir: str = "documentation"):
        """Save all generated diagrams"""
        output_path = self.rag_system_path / output_dir
        output_path.mkdir(exist_ok=True)
        
        # Check PlantUML availability
        plantuml_available = self.check_plantuml_installation()
        if not plantuml_available:
            print("⚠️  PlantUML not found, attempting to install Python package...")
            plantuml_available = self.install_plantuml_python()
        
        # Generate all diagrams
        diagrams = {
            'class_diagram.puml': self.generate_class_diagram(),
            'component_diagram.puml': self.generate_component_diagram(),
            'sequence_diagram.puml': self.generate_sequence_diagram(),
            'data_flow_diagram.puml': self.generate_data_flow_diagram(),
            'technology_stack.puml': self.generate_technology_stack()
        }
        
        # Save PlantUML files and generate PNGs
        for filename, content in diagrams.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Saved {filename}")
            
            # Generate PNG if PlantUML is available
            if plantuml_available:
                print(f"🖼️  Generating PNG for {filename}...")
                if self.generate_png_from_plantuml(file_path):
                    print(f"✅ Generated {filename.replace('.puml', '.png')}")
                else:
                    print(f"❌ Failed to generate PNG for {filename}")
            else:
                print(f"⚠️  Skipping PNG generation for {filename} (PlantUML not available)")
        
        # Save Mermaid diagrams
        mermaid_diagrams = self.generate_mermaid_diagrams()
        mermaid_file = output_path / 'mermaid_diagrams.json'
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            json.dump(mermaid_diagrams, f, indent=2)
        print(f"✅ Saved mermaid_diagrams.json")
        
        # Save analysis data
        analysis_data = {
            'classes': self.classes,
            'functions': self.functions,
            'relationships': self.relationships
        }
        analysis_file = output_path / 'code_analysis.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
        print(f"✅ Saved code_analysis.json")
        
        print(f"\n🎉 All diagrams saved to {output_path}")
        return output_path

def main():
    """Main function to generate UML diagrams"""
    print("🚀 Starting UML Diagram Generation for RAG System")
    print("=" * 50)
    
    generator = UMLGenerator()
    generator.analyze_codebase()
    output_path = generator.save_diagrams()
    
    print("\n📋 Generated Files:")
    for file in output_path.glob("*"):
        print(f"  - {file.name}")
    
    print("\n💡 Next Steps:")
    print("  1. View .png files for visual diagrams")
    print("  2. Use .puml files with PlantUML for editing")
    print("  3. Use mermaid_diagrams.json for web integration")
    print("  4. Include diagrams in documentation.html")

if __name__ == "__main__":
    main() 