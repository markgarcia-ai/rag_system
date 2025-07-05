import json
from typing import Dict, Any
from pathlib import Path

# Import the RAG engine (assume it's in the app directory)
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / 'app'))
from rag_engine import query_rag

class StockAgent:
    """
    StockAgent uses prompt engineering to interact with the RAG system and make stock trading decisions.
    It outputs a JSON decision and can call a (mock) market API to place an order.
    """
    def __init__(self, agent_name: str = "StockAgent"):
        self.agent_name = agent_name

    def craft_prompt(self, user_query: str, market: str = "S&P 500") -> str:
        """
        Create a prompt for the RAG system to get a stock decision.
        """
        prompt = (
            f"You are a stock trading agent. Your job is to analyze the following user query and market context, "
            f"and recommend a trading action in JSON format.\n"
            f"User Query: {user_query}\n"
            f"Market: {market}\n"
            f"Respond ONLY with a JSON object like: {{'action': 'buy'/'sell'/'hold', 'symbol': 'AAPL', 'amount': 10, 'reason': '...'}}.\n"
            f"If you don't have enough information, respond with: {{'action': 'hold', 'reason': 'Insufficient data'}}."
        )
        return prompt

    def get_decision(self, user_query: str, market: str = "S&P 500") -> Dict[str, Any]:
        """
        Query the RAG system and parse the JSON decision.
        """
        prompt = self.craft_prompt(user_query, market)
        rag_response = query_rag(prompt)
        try:
            # Try to extract JSON from the response
            start = rag_response.find('{')
            end = rag_response.rfind('}') + 1
            json_str = rag_response[start:end]
            decision = json.loads(json_str.replace("'", '"'))
        except Exception as e:
            decision = {"action": "hold", "reason": f"Failed to parse decision: {e}", "raw_response": rag_response}
        return decision

    def place_order(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock method to place an order via a market API.
        """
        # In a real implementation, this would call a broker API
        if decision.get("action") in ["buy", "sell"] and "symbol" in decision and "amount" in decision:
            # Simulate API call
            return {
                "status": "success",
                "order": decision,
                "message": f"Order placed: {decision['action']} {decision['amount']} shares of {decision['symbol']}"
            }
        else:
            return {
                "status": "no_action",
                "order": decision,
                "message": decision.get("reason", "No valid action taken.")
            }

# Example usage (for testing)
if __name__ == "__main__":
    agent = StockAgent()
    user_query = "Should I buy AAPL today?"
    decision = agent.get_decision(user_query, market="NASDAQ")
    print("Agent Decision:", decision)
    result = agent.place_order(decision)
    print("Order Result:", result) 