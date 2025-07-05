import time
import os
from llama_cpp import Llama

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the rag_system directory, then to models
model_path = os.path.join(script_dir, "..", "models", "mistral-7b-instruct-v0.1.Q2_K.gguf")
model_path = os.path.abspath(model_path)

llm = Llama(model_path=model_path, n_ctx=2048)

def generate_answer(prompt):
    start_time = time.time()
    
    # Count input tokens (approximate)
    input_tokens = len(prompt.split())  # Rough approximation
    
    response = llm(prompt, max_tokens=200)
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    # Count output tokens (approximate)
    output_text = response["choices"][0]["text"]
    output_tokens = len(output_text.split())  # Rough approximation
    
    return {
        "text": output_text,
        "generation_time": generation_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "tokens_per_second": (output_tokens / generation_time) if generation_time > 0 else 0
    }