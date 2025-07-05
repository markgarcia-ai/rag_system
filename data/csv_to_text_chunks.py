import os
import pandas as pd

MARKETS = [
    ('SP500', 'SP500_data', 'SP500_text'),
    ('NASDAQ', 'NASDAQ_data', 'NASDAQ_text'),
    ('SP600', 'SP600_data', 'SP600_text'),
    ('DOWJONES', 'DOWJONES_data', 'DOWJONES_text'),
    ('NYSE', 'NYSE_data', 'NYSE_text'),
    ('CRYPTO', 'CRYPTO_data', 'CRYPTO_text'),
]

for market, csv_dir_name, out_dir_name in MARKETS:
    CSV_DIR = os.path.join(os.path.dirname(__file__), csv_dir_name)
    OUT_DIR = os.path.join(os.path.dirname(__file__), out_dir_name)
    if not os.path.isdir(CSV_DIR):
        continue
    os.makedirs(OUT_DIR, exist_ok=True)
    for fname in os.listdir(CSV_DIR):
        if not fname.endswith('.csv'):
            continue
        ticker = fname.replace('.csv', '')
        df = pd.read_csv(os.path.join(CSV_DIR, fname))
        # Convert columns to numeric, coerce errors to NaN
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        lines = []
        for _, row in df.iterrows():
            # Skip rows with missing data
            if any(col not in row or pd.isna(row[col]) for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                continue
            line = (
                f"On {row['Date']}, {ticker} closed at ${row['Close']:.2f} "
                f"(Open: ${row['Open']:.2f}, High: ${row['High']:.2f}, "
                f"Low: ${row['Low']:.2f}, Volume: {int(row['Volume']):,})."
            )
            lines.append(line)
        with open(os.path.join(OUT_DIR, f'{ticker}.txt'), 'w') as f:
            f.write('\n'.join(lines))
    print(f"Converted all CSVs to text chunks in {OUT_DIR}") 