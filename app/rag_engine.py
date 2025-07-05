import time
from .embedding_model import query_embedding
from .llm_wrapper import generate_answer

def query_rag(question):
    results = query_embedding(question)
    context = "\n\n".join(results["documents"][0])
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    llm_response = generate_answer(prompt)
    return llm_response["text"]

def query_rag_debug(question):
    total_start_time = time.time()
    
    # Step 1: Embedding and Retrieval
    retrieval_start = time.time()
    results = query_embedding(question)
    retrieval_end = time.time()
    
    # Extract retrieved documents
    retrieved_docs = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if results["distances"] else []
    
    # Step 2: Context Building
    context_start = time.time()
    context = "\n\n".join(retrieved_docs)
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    context_end = time.time()
    
    # Step 3: LLM Generation
    generation_start = time.time()
    llm_response = generate_answer(prompt)
    generation_end = time.time()
    
    total_end_time = time.time()
    
    # Calculate timing breakdown
    context_building_time = context_end - context_start
    generation_time = generation_end - generation_start
    total_time = total_end_time - total_start_time
    
    # Return detailed debug information
    return {
        "question": question,
        "retrieved_documents": retrieved_docs,
        "similarity_distances": distances,
        "context": context,
        "prompt": prompt,
        "answer": llm_response["text"],
        "num_docs_retrieved": len(retrieved_docs),
        "context_length": len(context),
        
        # Timing information
        "timing": {
            "embedding_time": results.get("embedding_time", 0),
            "query_time": results.get("query_time", 0),
            "total_retrieval_time": results.get("total_retrieval_time", 0),
            "context_building_time": context_building_time,
            "generation_time": llm_response.get("generation_time", 0),
            "total_pipeline_time": total_time
        },
        
        # Token information
        "tokens": {
            "input_tokens": llm_response.get("input_tokens", 0),
            "output_tokens": llm_response.get("output_tokens", 0),
            "total_tokens": llm_response.get("total_tokens", 0),
            "tokens_per_second": llm_response.get("tokens_per_second", 0)
        },
        
        # Embedding information
        "embedding": {
            "model": results.get("embedding_model", "unknown"),
            "dimensions": results.get("embedding_dimensions", 0),
            "query_embedding_shape": f"({results.get('embedding_dimensions', 0)},)"
        },
        
        # Process breakdown
        "process_steps": [
            "1. Query embedding generation",
            "2. Vector similarity search",
            "3. Document retrieval",
            "4. Context building",
            "5. Prompt construction",
            "6. LLM text generation"
        ]
    }