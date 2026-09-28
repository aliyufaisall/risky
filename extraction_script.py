import os
import yfinance as yf
import pandas as pd

# 1. INITIALIZE CURRENCIES AND TARGET PATH
tickers = ["EURUSD=X", "GBPUSD=X"]
output_dir = "data"
output_path = os.path.join(output_dir, "processed_yfinance.csv")

print("📡 Connecting to financial markets to download live data...")

# FIX: Add group_by='ticker' to download each asset's columns together cleanly
raw_data = yf.download(tickers, period="2y", interval="1d", group_by='ticker')

# FIX: Flatten the multi-level column names down to just the Close price for each ticker
# This converts the complex columns into a single layer: ['EURUSD=X_Close', 'GBPUSD=X_Close']
close_columns = [f"{ticker}_Close" for ticker in tickers]
processed_df = pd.DataFrame()

for ticker in tickers:
    processed_df[f"{ticker}_Close"] = raw_data[ticker]['Close']

# 2. CALCULATE DAILY PERCENTAGE RETURNS
returns = processed_df.pct_change().dropna()

# Create data folder if missing, then overwrite the local file with today's metrics
os.makedirs(output_dir, exist_ok=True)
returns.to_csv(output_path)
print(f"💾 Live market data successfully cached to local disk at: {output_path}")

# 3. THE RE-LOADER (The engine loads it from disk to generate parameters)
print("\n⚙️ Loading cached data into active memory engine...")
stored_returns = pd.read_csv(output_path, index_col=0)

# Extract your exact Monte Carlo inputs on-the-fly
drift = stored_returns.mean()               
volatility = stored_returns.std()           
correlation_matrix = stored_returns.corr()  

print("\n--- PIPELINE METRICS GENERATED SUCCESSFULLY ---")
print(f"👉 Dynamic Daily Volatility (σ):\n{volatility}\n")
print(f"👉 Dynamic Correlation Matrix:\n{correlation_matrix}")
