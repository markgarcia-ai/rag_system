from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_documents(directory="data/example_docs"):
    docs = []
    for fname in os.listdir(directory):
        if fname.endswith(".txt"):
            with open(os.path.join(directory, fname), "r") as f:
                docs.append(f.read())
    return docs

def load_market_texts():
    market_dirs = [
        "data/SP500_text",
        "data/NASDAQ_text",
        "data/SP600_text",
        "data/DOWJONES_text",
        "data/NYSE_text",
        "data/CRYPTO_text",
    ]
    docs = []
    for directory in market_dirs:
        if not os.path.exists(directory):
            continue
        for fname in os.listdir(directory):
            if fname.endswith(".txt"):
                with open(os.path.join(directory, fname), "r") as f:
                    docs.append(f.read())
    return docs

def load_financial_concepts(path="data/financial_concepts.txt"):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [f.read()]

def split_documents(raw_texts):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.create_documents(raw_texts)

def ingest_docs():
    from .embedding_model import embedder, persist_embeddings
    texts = load_documents()
    texts += load_market_texts()
    texts += load_financial_concepts()
    chunks = split_documents(texts)
    persist_embeddings(chunks)