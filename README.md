# Offline RAG System

This is a fully local Retrieval-Augmented Generation (RAG) system built on:
- A quantized LLM using `llama.cpp`
- Embeddings from `sentence-transformers`
- Vector search via `ChromaDB`
- Flask backend and simple HTML frontend

## How to Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from app.document_loader import ingest_docs; ingest_docs()"
python main.py
open frontend/index.html
```

## Requirements
- macOS with Python 3.9+
- 8GB RAM minimum
- GGUF model in `models/` folder

You can download a 4-bit model like Mistral from Hugging Face and rename it to `mistral-7b.q4_0.gguf`.
