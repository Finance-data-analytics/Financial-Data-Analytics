from config import *
from data_retrieval import *  # Make sure this imports data for stocks and cryptos
from portfolio_analysis import recommend_portfolio
from plotting import *
from survey import evaluate_risk_aversion, suggest_portfolio

# Load the data back into a DataFrame
stocks_data = pd.read_excel("rendements_et_risques.xlsx", sheet_name="Stocks")
crypto_data = pd.read_excel("rendements_et_risques.xlsx", sheet_name="Crypto")

# Access the 'stocks_avg_daily_returns' and 'crypto_avg_daily_returns' from the DataFrames
stocks_avg_daily_returns = stocks_data["Rendement moyen"]
crypto_avg_daily_returns = crypto_data["Rendement moyen"]

# Plot the assets and CAL using the daily risk-free rate
plot_assets_and_cal_plotly(plotting_data, rf_daily)

# Evaluate the user's risk aversion
total_score = evaluate_risk_aversion()

# Then get the portfolio suggestion based on the survey score
portfolio_suggestion = suggest_portfolio(total_score)

# Prompt user for their capital and investment horizon
capital = float(input("Veuillez entrer votre capital à investir: "))
investment_horizon = int(input("Veuillez entrer votre horizon d'investissement (en années): "))

# Convert risk tolerance input to match expected values in recommend_portfolio
risk_tolerance_map = {'faible': 'low', 'moyenne': 'medium', 'élevée': 'high'}
risk_tolerance_input = input("Veuillez choisir votre tolérance au risque (faible, moyenne, élevée): ").lower()
risk_tolerance = risk_tolerance_map.get(risk_tolerance_input, 'low')

# Call the recommend_portfolio function with the user inputs
stock_investment, crypto_investment = recommend_portfolio(
    total_score,
    capital,
    investment_horizon,
    stocks_avg_daily_returns.values,  # Ensure these are numpy arrays
    crypto_avg_daily_returns.values,
    rf_daily  # You need to define this variable or replace it with the actual risk-free rate
)

# Display the suggested investment in stocks
print("\nRépartition du portefeuille d'actions:")
for i, amount in enumerate(stock_investment):
    if amount > 0:
        print(f"Stock {i}: {amount:.2f} USD")

# Display the suggested investment in cryptos
print("\nRépartition du portefeuille de cryptomonnaies:")
for i, amount in enumerate(crypto_investment):
    if amount > 0:
        print(f"Crypto {i}: {amount:.2f} USD")
