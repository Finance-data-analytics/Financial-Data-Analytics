from survey import *
from plotting import *


# Define a function to load data and extract relevant columns
def load_data(file_path, sheet_name, return_col, risk_col):
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    avg_daily_returns = data[return_col]
    volatility = data[risk_col]
    return avg_daily_returns, volatility


# Evaluate the user's risk aversion
def user_interaction_and_evaluation():
    total_score = evaluate_risk_aversion()
    portfolio_suggestion = suggest_portfolio(total_score)
    print(portfolio_suggestion)
    capital = float(input("Veuillez entrer votre capital à investir: "))
    investment_horizon = int(input("Veuillez entrer votre horizon d'investissement (en années): "))
    nb_stocks = int(input("Combien d'actif desirez vous au seins de votre portefeuille: "))

    return portfolio_suggestion, capital, investment_horizon, nb_stocks




def recommend_and_display_portfolio(portfolio_suggestion, capital, investment_horizon, nb_stocks):
    from data_retrieval import generate_plotting_data, recommend_portfolio
    plotting_data = generate_plotting_data(capital)
    # Call the recommend_portfolio function with the user inputs
    selected_stock_data = recommend_portfolio(
        nb_stocks,
        plotting_data["Stocks"]["data_stocks"],
        plotting_data["Cryptos"]["data_crypto"],
        capital,
        portfolio_suggestion,
        investment_horizon
    )
    return plotting_data,selected_stock_data
# Convert the annual risk-free rate to a daily rate
rf_annual = 0.0455  # 1% annual rate
rf_daily = (1 + rf_annual) ** (1 / 365) - 1
rf_daily

portfolio_suggestion, capital, investment_horizon, nb_stocks = user_interaction_and_evaluation()

plotting_data,selected_stock_data = recommend_and_display_portfolio(portfolio_suggestion, capital, investment_horizon, nb_stocks)
plot_assets_and_cal_plotly(plotting_data, rf_daily)
