from survey import *
from plotting import *
from main import *




def recommend_and_display_portfolio(portfolio_suggestion, capital, investment_horizon, nb_stocks):
    from data_retrieval import generate_plotting_data, recommend_portfolio
    plotting_data = generate_plotting_data(capital)
    # Call the recommend_portfolio function with the user inputs
    combined_selected_assets,monetary_allocation,best_weights = recommend_portfolio(
        nb_stocks,
        plotting_data["Stocks"]["data_stocks"],
        plotting_data["Cryptos"]["data_crypto"],
        capital,
        portfolio_suggestion,
        investment_horizon
    )
    return combined_selected_assets,monetary_allocation,best_weights
# Convert the annual risk-free rate to a daily rate
rf_annual = 0.0455  # 1% annual rate
rf_daily = (1 + rf_annual) ** (1 / 365) - 1
rf_daily
