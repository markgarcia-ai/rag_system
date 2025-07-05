from app.rag_engine import query_rag_debug
import os
import pandas as pd
from datetime import datetime, timedelta
import glob

class FinancialRAGAgent:
    """
    A simple financial agent that uses the RAG system to answer questions about stocks, financial concepts, and investment strategies.
    """
    def __init__(self):
        self.name = "Financial RAG Agent"
        self.description = (
            "An AI agent that can answer questions about S&P 500 stocks, financial concepts, and investment strategies using a Retrieval-Augmented Generation (RAG) system. "
            "It combines up-to-date market data, financial definitions, and LLM reasoning."
        )
        self.example_questions = [
            "What is the P/E ratio?",
            "How did AAPL perform in June 2024?",
            "Explain the difference between value and growth investing.",
            "What is a stop-loss order?",
            "What does it mean if a stock is overbought according to RSI?",
            "Summarize the recent performance of MSFT."
        ]

    def answer(self, question, market=None):
        # Pass market to query_rag_debug if needed in future
        return query_rag_debug(question)

class BrokerAgent:
    """
    An agent that acts as a broker, providing investment recommendations and guidance on the best stocks to invest in based on available data.
    """
    def __init__(self):
        self.name = "Broker Agent"
        self.description = (
            "An AI broker agent that analyzes S&P 500 stocks and recommends the best investment opportunities based on recent performance, trends, and financial indicators. "
            "It can answer questions about which stocks to buy, portfolio allocation, and general investment advice."
        )
        self.example_questions = [
            "What is the best stock to invest in right now?",
            "Which S&P 500 stock had the highest return last month?",
            "Recommend a diversified portfolio for a moderate risk investor.",
            "Should I buy AAPL or MSFT?",
            "What are the top 3 growth stocks currently?"
        ]

    def answer(self, question, market=None):
        # Use selected market's data directory
        base_dir = os.path.join(os.path.dirname(__file__), '../data')
        market_dirs = {
            'S&P 500': 'SP500_data',
            'NASDAQ': 'NASDAQ_data',
            'S&P 600': 'SP600_data',
            'Dow Jones': 'DOWJONES_data',
            'NYSE': 'NYSE_data',
            'Crypto': 'CRYPTO_data',
        }
        subdir = market_dirs.get(market, 'SP500_data')
        data_dir = os.path.join(base_dir, subdir)
        best_symbol = None
        best_return = float('-inf')
        best_start = None
        best_end = None
        today = datetime.now().date()
        one_month_ago = today - timedelta(days=30)
        if not os.path.isdir(data_dir):
            return {'answer': f"No data available for {market}.", 'agent': self.name}
        for fname in os.listdir(data_dir):
            if not fname.endswith('.csv'):
                continue
            symbol = fname.replace('.csv', '')
            try:
                df = pd.read_csv(os.path.join(data_dir, fname))
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date', 'Close'])
                df = df.sort_values('Date')
                recent = df[df['Date'] >= pd.Timestamp(one_month_ago)]
                if len(recent) < 2:
                    continue
                start_price = recent.iloc[0]['Close']
                end_price = recent.iloc[-1]['Close']
                ret = (end_price - start_price) / start_price * 100
                if ret > best_return:
                    best_return = ret
                    best_symbol = symbol
                    best_start = start_price
                    best_end = end_price
            except Exception as e:
                continue
        if best_symbol:
            answer = (f"Based on the last month of {market} data, the best stock to invest in is {best_symbol} "
                      f"with a return of {best_return:.2f}% (from ${best_start:.2f} to ${best_end:.2f}). "
                      f"This is based on recent price performance. For a personalized portfolio, please provide your risk tolerance and investment goals.")
        else:
            answer = f"Sorry, I could not determine the best stock to invest in for {market} due to insufficient data."
        return {
            'answer': answer,
            'agent': self.name
        }

def get_data_info():
    base_dir = os.path.join(os.path.dirname(__file__), '../data')
    market_dirs = {
        'S&P 500': 'SP500_data',
        'NASDAQ': 'NASDAQ_data',
        'S&P 600': 'SP600_data',
        'Dow Jones': 'DOWJONES_data',
        'NYSE': 'NYSE_data',
        'Crypto': 'CRYPTO_data',
    }
    markets_info = []
    for market, subdir in market_dirs.items():
        data_dir = os.path.join(base_dir, subdir)
        if not os.path.isdir(data_dir):
            continue
        num_stocks = 0
        min_date = None
        max_date = None
        for fname in glob.glob(os.path.join(data_dir, '*.csv')):
            num_stocks += 1
            try:
                df = pd.read_csv(fname)
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date'])
                if not df.empty:
                    stock_min = df['Date'].min().date()
                    stock_max = df['Date'].max().date()
                    if min_date is None or stock_min < min_date:
                        min_date = stock_min
                    if max_date is None or stock_max > max_date:
                        max_date = stock_max
            except Exception as e:
                continue
        markets_info.append({
            'market': market,
            'num_stocks': num_stocks,
            'min_date': str(min_date) if min_date else None,
            'max_date': str(max_date) if max_date else None
        })
    return {
        'markets': markets_info
    }

# For testing
if __name__ == "__main__":
    agent = FinancialRAGAgent()
    for q in agent.example_questions:
        print(f"Q: {q}")
        result = agent.answer(q)
        print(f"A: {result['answer']}\n---\n") 