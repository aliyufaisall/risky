import os
import numpy as np
import pandas as pd

# 1. LOAD THE CACHED DATA PIPELINES
input_dir = "data"
processed_path = os.path.join(input_dir, "processed_yfinance.csv")
raw_path = os.path.join(input_dir, "raw_prices.csv")

if not os.path.exists(processed_path) or not os.path.exists(raw_path):
    raise FileNotFoundError("❌ Please run data_pipeline.py first!")

stored_returns = pd.read_csv(processed_path, index_col=0)
stored_prices = pd.read_csv(raw_path, index_col=0)

# Identify our Spot and Futures data columns
spot_col = "EURUSD=X"
futures_col = "6E=F"

# 2. RUN THE COVARIANCE ENGINE FOR MVHR
# Calculate the covariance between Spot returns and Futures returns
covariance = stored_returns[spot_col].cov(stored_returns[futures_col])

# Calculate the variance of our hedging instrument (Futures)
futures_variance = stored_returns[futures_col].var()

# --- THE CALCULATED IMPORTER MVHR ---
mvhr = covariance / futures_variance

# 3. RUN MONTE CARLO VALUE AT RISK (VaR)
start_spot_price = float(stored_prices[spot_col].iloc[-1])
eur_drift = stored_returns[spot_col].mean()               
eur_volatility = stored_returns[spot_col].std()           

num_simulations = 10000  
time_horizon = 30        
euro_invoice_exposure = 1000000  # €1,000,000 invoice due
baseline_cost_usd = euro_invoice_exposure * start_spot_price 

random_shocks = np.random.normal(0, 1, (time_horizon, num_simulations))
simulated_paths = np.zeros((time_horizon + 1, num_simulations))
simulated_paths[0] = start_spot_price

for t in range(1, time_horizon + 1):
    exponent = (eur_drift - 0.5 * (eur_volatility ** 2)) + (eur_volatility * random_shocks[t-1])
    simulated_paths[t] = simulated_paths[t-1] * np.exp(exponent)

final_prices = simulated_paths[-1]
final_portfolio_values = euro_invoice_exposure * final_prices
simulated_losses = final_portfolio_values - baseline_cost_usd
monte_carlo_var_95 = np.percentile(simulated_losses, 95)

# --- 4. STEP 3: COST ENGINE ---
fed_rate, ecb_rate = 0.0400, 0.0250
hedging_cost = baseline_cost_usd * abs(ecb_rate - fed_rate) * (time_horizon / 360)

# --- FINAL SYSTEM PRINTOUT ---
print("\n==============================================")
print("🏁 ENTERPRISE RISK MODEL FOR US IMPORTERS")
print("==============================================")
print(f"📈 Baseline Invoice Cost Today : ${baseline_cost_usd:,.2f} USD")
print(f"⚠️ Unhedged Value at Risk (95%): ${monte_carlo_var_95:,.2f} USD")
print(f"🎯 Calculated Importer MVHR    : {mvhr:.2%}")
print(f"💼 Target Contract Size to Buy : €{euro_invoice_exposure * mvhr:,.2f} Euros")
print(f"💰 Out-of-pocket Forward Cost  : ${hedging_cost:,.2f} USD")
print("==============================================")

# --- STEP 4: HEDGED VALUE AT RISK (HEDGED VaR) ---
print("\n--- STEP 4: NET HEDGED RISK MANAGEMENT SUMMARY ---")

# Calculate remaining currency risk based on how much was left unhedged
unhedged_ratio = 1.0 - (mvhr)  # If mvhr is 100% (1.0), this is 0.0
remaining_currency_risk = monte_carlo_var_95 * unhedged_ratio

# Total economic impact is your remaining currency risk PLUS the guaranteed cost of the hedge
total_hedged_var = remaining_currency_risk + hedging_cost

print(f"📉 Remaining Open Currency Risk : ${remaining_currency_risk:,.2f} USD")
print(f"🛡️ Total Hedged VaR (Net Risk)   : ${total_hedged_var:,.2f} USD")
print(f"💡 Executive Verdict: By deploying this hedge, you have capped your absolute")
print(f"                      worst-case extra expense at a fixed ${total_hedged_var:,.2f},")
print(f"                      saving your company a potential ${monte_carlo_var_95 - total_hedged_var:,.2f} in tail-risk losses.")
print("==============================================")
