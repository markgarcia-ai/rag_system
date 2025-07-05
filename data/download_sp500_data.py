import os
import sys
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup

MARKET_CONFIG = {
    'SP500': {
        'name': 'S&P 500',
        'data_dir': 'SP500_data',
        'wiki_url': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
        'table_id': 'constituents',
        'ticker_col': 0,
    },
    'NASDAQ': {
        'name': 'NASDAQ',
        'data_dir': 'NASDAQ_data',
        'wiki_url': None,  # Use static list
        'table_id': None,
        'ticker_col': None,
    },
    'SP600': {
        'name': 'S&P 600',
        'data_dir': 'SP600_data',
        'wiki_url': 'https://en.wikipedia.org/wiki/List_of_S%26P_600_companies',
        'table_id': 'constituents',
        'ticker_col': 0,
    },
    'DOWJONES': {
        'name': 'Dow Jones',
        'data_dir': 'DOWJONES_data',
        'wiki_url': 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average',
        'table_id': None,  # Use first table
        'ticker_col': 1,  # 2nd column
    },
    'NYSE': {
        'name': 'NYSE',
        'data_dir': 'NYSE_data',
        'wiki_url': None,  # Not easily available; user must provide tickers
        'table_id': None,
        'ticker_col': None,
    },
}

def get_tickers(market):
    config = MARKET_CONFIG[market]
    if market == 'NASDAQ':
        # Use static list from NASDAQ_data/tickers.txt
        tickers_path = os.path.join(os.path.dirname(__file__), 'NASDAQ_data', 'tickers.txt')
        if not os.path.exists(tickers_path):
            print('Please provide NASDAQ-100 tickers in NASDAQ_data/tickers.txt (one per line)')
            return []
        with open(tickers_path) as f:
            return [line.strip() for line in f if line.strip()]
    elif config['wiki_url']:
        url = config['wiki_url']
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        if config['table_id']:
            table = soup.find('table', {'id': config['table_id']})
        else:
            table = soup.find_all('table')[0]
        tickers = []
        for row in table.find_all('tr')[1:]:
            tds = row.find_all('td')
            if len(tds) > config['ticker_col']:
                ticker = tds[config['ticker_col']].text.strip().replace('.', '-')
                if ticker:
                    tickers.append(ticker)
        return tickers
    elif market == 'NYSE':
        # NYSE: user must provide a tickers.txt file in the data dir
        tickers_path = os.path.join(os.path.dirname(__file__), 'NYSE_data', 'tickers.txt')
        if not os.path.exists(tickers_path):
            print('Please provide NYSE tickers in NYSE_data/tickers.txt (one per line)')
            return []
        with open(tickers_path) as f:
            return [line.strip() for line in f if line.strip()]
    else:
        return []

def download_and_save_ticker(ticker, data_dir):
    print(f"Downloading {ticker}...")
    try:
        df = yf.download(ticker, period='2y', interval='1d', auto_adjust=True)
        if df.empty:
            print(f"No data for {ticker}")
            return
        df.reset_index(inplace=True)
        df['Ticker'] = ticker
        out_path = os.path.join(data_dir, f"{ticker}.csv")
        df.to_csv(out_path, index=False)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")

def main():
    market = sys.argv[1].upper() if len(sys.argv) > 1 else 'SP500'
    if market not in MARKET_CONFIG:
        print(f"Unknown market: {market}. Choose from: {list(MARKET_CONFIG.keys())}")
        return
    config = MARKET_CONFIG[market]
    data_dir = os.path.join(os.path.dirname(__file__), config['data_dir'])
    os.makedirs(data_dir, exist_ok=True)
    tickers = get_tickers(market)
    print(f"Found {len(tickers)} tickers for {config['name']}")
    for ticker in tickers:
        download_and_save_ticker(ticker, data_dir)

# Instructions for static tickers:
# For NASDAQ: Place NASDAQ-100 tickers in rag_system/data/NASDAQ_data/tickers.txt, one per line.
# For NYSE: Place NYSE tickers in rag_system/data/NYSE_data/tickers.txt, one per line.

if __name__ == "__main__":
    main() 