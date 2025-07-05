import time
from sentence_transformers import SentenceTransformer
import chromadb

embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="docs")

def persist_embeddings(chunks):
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode([chunk.page_content])[0]
        collection.add(documents=[chunk.page_content], embeddings=[embedding.tolist()], ids=[str(i)])

def query_embedding(question, k=3):
    start_time = time.time()
    
    # Generate query embedding
    q_embed = embedder.encode([question])[0]
    embedding_time = time.time() - start_time
    
    # Query the database
    query_start = time.time()
    results = collection.query(query_embeddings=[q_embed.tolist()], n_results=k)
    query_time = time.time() - query_start
    
    # Add timing and embedding info to results
    results["embedding_time"] = embedding_time
    results["query_time"] = query_time
    results["total_retrieval_time"] = embedding_time + query_time
    results["embedding_dimensions"] = len(q_embed)
    results["embedding_model"] = "all-MiniLM-L6-v2"
    
    return results