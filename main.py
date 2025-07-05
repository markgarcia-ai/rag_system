import socket
from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
from app.rag_engine import query_rag
from app.financial_agent import FinancialRAGAgent, BrokerAgent, get_data_info

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "")
    answer = query_rag(question)
    return jsonify({"answer": answer})

@app.route("/chat_debug", methods=["POST"])
def chat_debug():
    data = request.get_json()
    question = data.get("question", "")
    agent_type = data.get("agent", "financial")
    market = data.get("market", "S&P 500")

    if agent_type == "broker":
        agent = BrokerAgent()
        result = agent.answer(question, market=market)
        # BrokerAgent returns a dict with 'answer' and 'agent', wrap for debug panel
        debug_info = {
            'answer': result['answer'],
            'agent': result['agent'],
            'question': question,
            'retrieved_documents': [],
            'similarity_distances': [],
            'context': '',
            'prompt': '',
            'timing': {},
            'tokens': {},
            'embedding': {},
            'process_steps': [f"BrokerAgent used for this query. Market: {market}"],
            'num_docs_retrieved': 0,
            'context_length': 0,
        }
    else:
        agent = FinancialRAGAgent()
        debug_info = agent.answer(question, market=market)
    return jsonify(debug_info)

@app.route("/data_info", methods=["GET"])
def data_info():
    info = get_data_info()
    return jsonify(info)

@app.route("/", methods=["GET"])
def root():
    return redirect("/frontend/index.html")

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    return send_from_directory("frontend", filename)

def find_free_port(start_port=5000, max_tries=20):
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No free ports found")

if __name__ == "__main__":
    try:
        port = find_free_port(start_port=5000, max_tries=20)
        print(f"🚀 RAG System starting on http://127.0.0.1:{port}")
        print(f"📱 Frontend available at: http://127.0.0.1:{port}")
        print(f"🔧 API endpoints:")
        print(f"   - POST /chat - Basic chat")
        print(f"   - POST /chat_debug - Chat with debug info")
        print(f"   - GET /data_info - Market data info")
        print("=" * 50)
        app.run(debug=True, port=port, host="127.0.0.1")
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        print("💡 Try manually specifying a port or check what's using the ports")
        exit(1)