import os
import pandas as pd
from datetime import datetime, timedelta
import sys

# Try to import CoinDatabase from cyrpto_bot, fallback to yfinance if not available
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../cyrpto_bot/src')))
    from data.coin_database import CoinDatabase
    coin_db = CoinDatabase(mode='coingecko')
    use_coin_db = True
except Exception as e:
    print(f"CoinDatabase not available: {e}")
    use_coin_db = False
    import yfinance as yf

# List of main coins to export
MAIN_COINS = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'MATIC',
    'LINK', 'UNI', 'ATOM', 'LTC', 'INJ', 'OP', 'ARB', 'SEI', 'USDT', 'USDC'
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'CRYPTO_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

for symbol in MAIN_COINS:
    print(f"Exporting {symbol}...")
    try:
        if use_coin_db:
            df = coin_db.get_historical_data(symbol, start_time=datetime.strptime(start_date, '%Y-%m-%d'), end_time=datetime.strptime(end_date, '%Y-%m-%d'))
            if df.empty:
                print(f"No data for {symbol}")
                continue
            df = df.rename(columns={
                'timestamp': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume',
                'market_cap': 'Market Cap'
            })
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        else:
            # Fallback: use yfinance (for coins with -USD tickers)
            ticker = symbol + '-USD'
            data = yf.download(ticker, start=start_date, end=end_date)
            if data.empty:
                print(f"No data for {symbol}")
                continue
            df = data.reset_index()
            df = df.rename(columns={
                'Date': 'Date',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume',
            })
            df['Market Cap'] = None  # yfinance does not provide market cap for crypto
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        # Save to CSV
        out_path = os.path.join(OUTPUT_DIR, f"{symbol}.csv")
        df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap']].to_csv(out_path, index=False)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Error exporting {symbol}: {e}") 