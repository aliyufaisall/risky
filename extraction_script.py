import os
import yfinance as yf
import pandas as pd

# 1. INITIALIZE ASSETS
# EURUSD=X is the Spot rate. 6E=F is the highly liquid CME Euro Futures contract ticker.
tickers = ["EURUSD=X", "6E=F"]
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

print("📡 Downloading Spot and Futures market data...")
raw_data = yf.download(tickers, period="2y", interval="1d", group_by='ticker')

# Flatten multi-level data
prices_df = pd.DataFrame()
for t in tickers:
    prices_df[t] = raw_data[t]['Close']

# Drop missing days and calculate clean percentage returns
prices_df = prices_df.dropna()
returns_df = prices_df.pct_change().dropna()

# Save data arrays to disk
prices_df.to_csv(os.path.join(output_dir, "raw_prices.csv"))
returns_df.to_csv(os.path.join(output_dir, "processed_yfinance.csv"))

print(f"💾 Success! Saved raw prices and returns to \\{output_dir}\\")
