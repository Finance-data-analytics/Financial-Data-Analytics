from config import *
from data_retrieval import *  # Make sure this imports data for stocks and cryptos
from portfolio_analysis import recommend_portfolio
from plotting import *
from survey import evaluate_risk_aversion, suggest_portfolio


# Define a function to load data and extract relevant columns
def load_data(file_path, sheet_name, return_col, risk_col):
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    avg_daily_returns = data[return_col]
    volatility = data[risk_col]
    return avg_daily_returns, volatility


# File path and column names
file_path = "rendements_et_risques.xlsx"
return_col = "Rendement moyen"
risk_col = "Risque"

# Load and process data for stocks and crypto
stocks_avg_daily_returns, stocks_volatility = load_data(file_path, "Stocks", return_col, risk_col)
crypto_avg_daily_returns, crypto_volatility = load_data(file_path, "Crypto", return_col, risk_col)


# Evaluate the user's risk aversion
def user_interaction_and_evaluation():
    total_score = evaluate_risk_aversion()
    portfolio_suggestion = suggest_portfolio(total_score)
    print(portfolio_suggestion)

    capital = float(input("Veuillez entrer votre capital à investir: "))
    investment_horizon = int(input("Veuillez entrer votre horizon d'investissement (en années): "))
    nb_stocks = int(input("Veuillez entrer un nombre de stocks que vous desirez avoir dans votre portefeuille: "))

    return total_score, capital, investment_horizon, nb_stocks


def recommend_and_display_portfolio(total_score, capital, investment_horizon, nb_stocks):
    # Call the recommend_portfolio function with the user inputs
    stock_investment, crypto_investment = recommend_portfolio(
        total_score,
        capital,
        investment_horizon,
        stocks_avg_daily_returns.values,
        stocks_volatility,
        crypto_avg_daily_returns.values,
        crypto_volatility,
        rf_daily,  # This should be defined or replaced with the actual risk-free rate
        plotting_data["Stocks"]["list_ticker_isin"],
        plotting_data["Cryptos"]["list_crypto"],
        nb_stocks
    )

    # Displaying the portfolio allocation
    print("\nRecommended Portfolio Allocation:")

    # Display for stocks
    print("\nStocks Investment:")
    for stock, amount in zip(plotting_data["Stocks"]["symbols"], stock_investment):
        if amount > 0:
            print(f"{stock}: {amount:.2f} USD")

    # Display for cryptocurrencies
    print("\nCryptocurrency Investment:")
    for crypto, amount in zip(plotting_data["Cryptos"]["symbols"], crypto_investment):
        if amount > 0:
            print(f"{crypto}: {amount:.2f} USD")

    # Calculate and display the total percentage invested in stocks and cryptos
    percentage_in_stocks = (sum(stock_investment) / capital) * 100
    percentage_in_cryptos = (sum(crypto_investment) / capital) * 100

    print(f"\nTotal Portfolio Distribution:\n - Stocks: {percentage_in_stocks:.2f}%\n - Cryptocurrencies: {percentage_in_cryptos:.2f}%")


# Plot the assets and CAL using the daily risk-free rate
plot_assets_and_cal_plotly(plotting_data, rf_daily)
