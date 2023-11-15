from config import *
from data_retrieval import *
from portfolio_analysis import *
from plotting import *

# Load the data back into a DataFrame
stocks_data = pd.read_excel("rendements_et_risques.xlsx", sheet_name="Stocks")
crypto_data = pd.read_excel("rendements_et_risques.xlsx", sheet_name="Crypto")

# Now you can access `stocks_avg_daily_returns` and `crypto_avg_daily_returns` from the DataFrames
stocks_avg_daily_returns = stocks_data["Rendement moyen"]
crypto_avg_daily_returns = crypto_data["Rendement moyen"]

capital = float(input("Veuillez entrer votre capital à investir: "))
investment_horizon = int(input("Veuillez entrer votre horizon d'investissement (en années): "))
risk_tolerance = input("Veuillez choisir votre tolérance au risque (faible, moyenne, élevée): ")

# Plot the assets and CAL using the daily risk-free rate
plot_assets_and_cal_plotly(plotting_data, rf_daily)

# Récupération des noms des stocks et des cryptos depuis les fichiers Excel
print(crypto_data.columns)
crypto_names = crypto_data.columns.tolist()
stock_data = pd.read_excel("stocks.xlsx")
stock_names = stock_data['Name'].tolist()  # Assuming your Excel file for stocks contains a 'Name' column for stock names.

# Récupération de l'investissement recommandé
stock_investment, crypto_investment = recommend_portfolio(
    capital, 
    investment_horizon, 
    risk_tolerance, 
    stocks_avg_daily_returns, 
    crypto_avg_daily_returns,
    stocks_daily_returns, # Assuming this is needed based on your portfolio_analysis.py
    crypto_daily_returns  # Assuming this is needed based on your portfolio_analysis.py
)

# Affichage de la répartition du portefeuille d'actions
print("\nRépartition du portefeuille d'actions :")
for ticker, name, amount in zip(first_100_stocks, stock_names, stock_investment):
    if amount > 0:
        print(f"{name} ({ticker}): {amount:.2f} USD")

# Affichage de la répartition du portefeuille de cryptomonnaies
print("\nRépartition du portefeuille de cryptomonnaies :")
for ticker, name, amount in zip(crypto_symbols, crypto_names, crypto_investment):
    if amount > 0:
        print(f"{name} ({ticker}): {amount:.2f} USD")
