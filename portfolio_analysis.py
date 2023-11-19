from data_retrieval import *
import numpy as np
import matplotlib.pyplot as plt


def portfolio_volatility(weights, avg_returns, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


def calculate_returns(data):
    # Forward fill missing values
    data_ffilled = data.ffill()

    # Calculate percentage change
    returns = data_ffilled.ffill().pct_change()

    # Drop any remaining NaN values
    returns_cleaned = returns.dropna()

    # Create an explicit copy to avoid SettingWithCopyWarning
    returns_cleaned = returns_cleaned.copy()

    # Replace infinities and recheck for NaNs
    returns_cleaned.replace([np.inf, -np.inf], np.nan, inplace=True)
    returns_cleaned.dropna(inplace=True)

    return returns_cleaned


def efficient_frontier(returns, target_return_, min_diversification=0):
    if returns.isnull().values.any() or np.isinf(returns).values.any():
        raise ValueError("Input returns contain NaN or infinite values")

    cov_matrix = returns.cov()
    avg_returns = returns.mean()

    # Check again for NaNs or Infinities in avg_returns
    if avg_returns.isna().any() or np.isinf(avg_returns).any():
        raise ValueError("Average returns contain NaN or infinite values")

    num_assets = len(returns.columns)
    args = (avg_returns, cov_matrix)

    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: np.sum(x * avg_returns) - target_return_}
    ]

    if min_diversification:
        constraints.append({'type': 'eq', 'fun': lambda weights: np.sum(weights) - min_diversification})

    bounds = tuple((0, 1) for _ in range(num_assets))

    # Consider adding options to the minimize function for better convergence
    results = minimize(portfolio_volatility, num_assets * [1. / num_assets, ], args=args, method='SLSQP',
                       constraints=constraints, bounds=bounds)
    return results


# Function to perform Monte Carlo simulation for stock selection
def monte_carlo_selection(stocks_data, nb_simulations, nb_stocks):
    best_sharpe_ratio = -np.inf
    all_weights = np.zeros((nb_simulations, len(stocks_data.columns)))
    ret_arr = np.zeros(nb_simulations)
    vol_arr = np.zeros(nb_simulations)
    sharpe_arr = np.zeros(nb_simulations)

    for i in range(nb_simulations):
        weights = np.random.random(len(stocks_data.columns))
        weights /= np.sum(weights)
        all_weights[i, :] = weights

        # Calculate portfolio return and volatility
        daily_returns = (stocks_data.pct_change().dropna()).dot(weights)
        annual_return = daily_returns.mean() * 252
        annual_volatility = daily_returns.std() * np.sqrt(252)

        # Update the returns, volatilities, and Sharpe Ratios
        ret_arr[i] = annual_return
        vol_arr[i] = annual_volatility
        sharpe_arr[i] = annual_return / annual_volatility

        # Track the best Sharpe Ratio and corresponding weights
        if sharpe_arr[i] > best_sharpe_ratio:
            best_sharpe_ratio = sharpe_arr[i]
            best_stocks_weights = weights

    # Select stocks based on the best Sharpe Ratio
    best_stocks_indices = best_stocks_weights.argsort()[-nb_stocks:]
    selected_stocks = stocks_data.columns[best_stocks_indices]

    return selected_stocks, ret_arr, vol_arr, sharpe_arr


# Function to perform Monte Carlo simulation for weight allocation in the selected stocks
def monte_carlo_allocation(selected_stocks_data, nb_simulations):
    best_sharpe_ratio = -np.inf
    all_weights = np.zeros((nb_simulations, len(selected_stocks_data.columns)))
    ret_arr = np.zeros(nb_simulations)
    vol_arr = np.zeros(nb_simulations)
    sharpe_arr = np.zeros(nb_simulations)

    for i in range(nb_simulations):
        print(i)
        weights = np.random.random(len(selected_stocks_data.columns))
        weights /= np.sum(weights)
        all_weights[i, :] = weights

        # Calculate portfolio return and volatility
        daily_returns = (selected_stocks_data.pct_change().dropna()).dot(weights)
        annual_return = daily_returns.mean() * 252
        annual_volatility = daily_returns.std() * np.sqrt(252)

        # Update the returns, volatilities, and Sharpe Ratios
        ret_arr[i] = annual_return
        vol_arr[i] = annual_volatility
        sharpe_arr[i] = annual_return / annual_volatility

        # Track the best Sharpe Ratio and corresponding weights
        if sharpe_arr[i] > best_sharpe_ratio:
            best_sharpe_ratio = sharpe_arr[i]
            best_weights = weights

    return best_weights, ret_arr, vol_arr, sharpe_arr


def recommend_portfolio(nb_stocks, list_stock,list_crypto,data_stock,data_crypto, capital,
                        total_score,
                        investment_horizon):

    # Drop any NaN values to clean the data
    stocks_data = data_stock.dropna()

    crypto_data = data_crypto.dropna()
    combined_data = pd.concat([data_stock, crypto_data], axis=1)

    selected_assets, ret_arr_selection, vol_arr_selection, sharpe_arr_selection = monte_carlo_selection(combined_data,
                                                                                                        10000,
                                                                                                        nb_stocks)

    # Extract the data for the selected stocks
    selected_assets_data = combined_data[selected_assets]

    # Run the second Monte Carlo simulation for weight allocation
    best_weights, ret_arr_allocation, vol_arr_allocation, sharpe_arr_allocation = monte_carlo_allocation(
        selected_assets_data, 10000)

    nb_cryptos = len(list_crypto)

    # Adjust the crypto weights based on the investor's risk profile
    crypto_weight_limit = get_crypto_weight_limit(total_score, investment_horizon)
    crypto_weights = best_weights[-nb_cryptos:]  # Assuming the last weights are for cryptos
    stocks_weights = best_weights[:-nb_cryptos]

    if crypto_weights.sum() > crypto_weight_limit:
        # Scale down crypto weights if they exceed the limit
        excess_weight = crypto_weights.sum() - crypto_weight_limit
        crypto_weights *= (crypto_weight_limit / crypto_weights.sum())
        stocks_weights += (excess_weight / len(stocks_weights))  # Reallocate excess weight to stocks
        best_weights = np.concatenate([stocks_weights, crypto_weights])

    # Scale the weights by the user's capital
    monetary_allocation = best_weights * capital

    # Print the monetary allocation for the selected stocks and cryptos
    print("Monetary allocation for the Best Portfolio:")
    for asset, allocation in zip(selected_assets, monetary_allocation):
        print(f"{asset}: ${allocation:,.2f}")

    # Loop through each stock and its weight to print them
    for stock, weight in zip(selected_assets_data, best_weights):
        print(f"{stock}: {weight:.2%}")
    # Plot the results of the first Monte Carlo simulation
    plt.figure(figsize=(12, 8))
    plt.scatter(vol_arr_selection, ret_arr_selection, c=sharpe_arr_selection, cmap='plasma')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.title('All Combinations of Stocks')
    plt.show()

    # Plot the results of the second Monte Carlo simulation
    plt.figure(figsize=(12, 8))
    plt.scatter(vol_arr_allocation, ret_arr_allocation, c=sharpe_arr_allocation, cmap='plasma')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.title('Optimal Weight Allocation for Selected Stocks')

    # Highlight the best portfolio with a red dot
    max_sharpe_idx = sharpe_arr_allocation.argmax()  # Index of the portfolio with the highest Sharpe Ratio
    plt.scatter(vol_arr_allocation[max_sharpe_idx], ret_arr_allocation[max_sharpe_idx], c='red', s=50,
                edgecolors='black', label='Best Portfolio')

    # Show plot with legend
    plt.legend()
    plt.show()

    # Print the stock names and the corresponding weights of the best portfolio
    print("Stocks and their weights in the Best Portfolio:")



def get_crypto_weight_limit(total_score, investment_horizon):
    # Define the logic to determine the crypto weight limit based on the total_score and investment_horizon
    # This is a placeholder function; you'll need to implement the actual logic based on your requirements
    if total_score < 10 :
        return 0
    elif total_score >= 10 and total_score < 15 :
        return 0.10  # Low risk tolerance
    elif total_score >= 15 and total_score <20 :
        return 0.20  # Medium risk tolerance
    elif total_score > 20 :
        return 0.30  # High risk tolerance
# def recommend_portfolio(score, capital, investment_horizon, stocks_avg_daily_returns, stocks_volatility,
#                         crypto_avg_daily_returns, crypto_volatility, rf_daily, stocks_info, crypto_info, nb_stocks):
#     # max_crypto_weight, risk_tolerance = define_max_crypto_weight(score, investment_horizon)
#     #
#     # # Récupération des prix des stocks
#     # # stock_prices = {identifier: yf.download(identifier, period="5d")['Adj Close'].iloc[-1] for identifier in stocks_info}
#     #
#     # # Optimisation initiale du portefeuille
#     # stock_weights, crypto_weights = optimize_portfolio(capital, max_crypto_weight, stocks_avg_daily_returns,
#     #                                                    stocks_volatility, crypto_avg_daily_returns, crypto_volatility,
#     #                                                    rf_daily, risk_tolerance)
#     #
#     # if not any(crypto_weight > 0 for crypto_weight in crypto_weights):
#     #     stock_weights = optimize_only_stocks(risk_tolerance, stocks_avg_daily_returns, stocks_volatility, rf_daily)
#     # # Ajustement pour les parts entières et calcul du capital restant
#     # # stock_weights, remaining_capital = adjust_for_whole_shares(stock_weights, stock_prices, capital)
#     #
#     # # Calcul des investissements finaux
#     # stock_investment = np.array(stock_weights) * capital
#     # crypto_investment = np.array(crypto_weights) * capital
#     num_simulations = 5000
#     prices = yf.download(stocks_info, start='2019-01-01', end='2023-11-17')['Adj Close']
#     print("Téléchargement des prix des actions terminé.")
#     print("Premières lignes des prix des actions :", prices.head())
#
#     return_data = prices.pct_change().dropna()
#     print("Données de rendement calculées.")
#     latest_prices = prices.iloc[-1]
#
#     ret_arr, vol_arr, sharpe_arr, all_weights = monte_carlo_simulation(return_data, num_simulations, capital, rf_daily,latest_prices)
#     print("Simulation de Monte Carlo terminée.")
#     # Affichage des résultats
#     plt.figure(figsize=(12, 8))
#     plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='plasma')
#     plt.colorbar(label='Sharpe Ratio')
#     plt.xlabel('Volatility')
#     plt.ylabel('Return')
#     plt.show()
#     return
#
#
# # Fonction pour simuler des répartitions de portefeuille
# def monte_carlo_simulation(return_data, num_simulations, capital, rf_daily, latest_prices):
#     num_stocks = len(latest_prices)
#     all_weights = np.zeros((num_simulations, num_stocks))
#     ret_arr = np.zeros(num_simulations)
#     vol_arr = np.zeros(num_simulations)
#     sharpe_arr = np.zeros(num_simulations)
#
#     for i in range(num_simulations):
#         # Génération de poids aléatoires
#         weights = np.random.random(num_stocks)
#         weights /= np.sum(weights)
#
#         # Ajustement pour les parts entières d'actions
#         if not latest_prices.empty and not latest_prices.isna().any():
#             adjusted_weights, _ = adjust_for_whole_shares(weights, latest_prices, capital)
#
#             # S'assurer que les poids ajustés correspondent à la taille attendue
#             if len(adjusted_weights) != num_stocks:
#                 raise ValueError("La taille des poids ajustés ne correspond pas au nombre d'actions")
#
#             # Calcul de la performance du portefeuille
#             portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_performance(adjusted_weights, return_data, rf_daily)
#
#             # Stockage des résultats
#             all_weights[i, :] = adjusted_weights
#             ret_arr[i] = portfolio_return
#             vol_arr[i] = portfolio_volatility
#             sharpe_arr[i] = sharpe_ratio
#
#             # Affichage des résultats de la simulation actuelle
#             print(f"Simulation {i+1}/{num_simulations}")
#             print(f"Rendement: {portfolio_return:.4f}")
#             print(f"Volatilité: {portfolio_volatility:.4f}")
#             print(f"Ratio de Sharpe: {sharpe_ratio:.4f}\n")
#         else:
#             pass
#
#     return ret_arr, vol_arr, sharpe_arr, all_weights
#
#
#
# def adjust_for_whole_shares(weights, latest_prices, capital):
#     adjusted_weights = []
#     used_capital = 0
#
#     for ticker, weight in zip(latest_prices.index, weights):
#         stock_price = latest_prices[ticker]
#         stock_amount = weight * capital
#         num_shares = int(stock_amount / stock_price)
#         adjusted_weight = num_shares * stock_price
#         adjusted_weights.append(adjusted_weight / capital)
#         used_capital += adjusted_weight
#
#     remaining_capital = capital - used_capital
#
#     return adjusted_weights, remaining_capital
#
#
#
#
# def calculate_portfolio_performance(weights, return_data, rf_daily):
#     # Assurez-vous que les poids sont un tableau NumPy
#     if not isinstance(weights, np.ndarray):
#         weights = np.array(weights)
#
#     # Calcul du rendement et de la volatilité du portefeuille
#     portfolio_return = np.sum(weights * return_data.mean()) * 252
#     portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(return_data.cov() * 252, weights)))
#     sharpe_ratio = (portfolio_return - rf_daily) / portfolio_volatility
#
#     return portfolio_return, portfolio_volatility, sharpe_ratio
#
#
#
#
# def select_stocks(stocks_avg_daily_returns, stocks_volatility, rf_daily, nb_stocks):
#     # Calcul du ratio de Sharpe pour chaque stock
#     sharpe_ratios = (stocks_avg_daily_returns - rf_daily) / stocks_volatility
#
#     # Sélection des nb_stocks ayant les meilleurs ratios de Sharpe
#     selected_indices = sharpe_ratios.nlargest(nb_stocks).index
#
#     return selected_indices
# def reoptimize_portfolio(current_weights, stock_prices, capital, stocks_avg_daily_returns, stocks_volatility, rf_daily,
#                          risk_tolerance):
#     remaining_capital = capital - sum(weight * capital for weight in current_weights)
#     num_stocks = len(stocks_avg_daily_returns)
#
#     def negative_sharpe_ratio(weights):
#         # Utilisez les variables du contexte pour calculer le ratio de Sharpe négatif
#         portfolio_return = np.dot(weights, stocks_avg_daily_returns)
#         portfolio_vol = np.sqrt(np.dot(weights ** 2, stocks_volatility ** 2))
#         sharpe_ratio = (portfolio_return - rf_daily) / portfolio_vol
#         return -sharpe_ratio
#
#     # Contraintes pour garantir que la somme des poids est égale au capital restant
#     constraints = [
#         {'type': 'eq', 'fun': lambda x: np.sum(x) - remaining_capital / capital},
#         # Autres contraintes basées sur la tolérance au risque
#     ]
#
#     # Bornes pour chaque action
#     bounds = [(0, 1) for _ in range(num_stocks)]
#
#     # Initialisation des poids pour la réoptimisation
#     init_guess = [(weight * capital + remaining_capital / num_stocks) / capital for weight in current_weights]
#
#     # Exécution de l'optimisation avec les nouvelles contraintes
#     opt_results = minimize(
#         negative_sharpe_ratio, init_guess,
#         method='SLSQP', bounds=bounds, constraints=constraints
#     )
#
#     # Ajustement final pour s'assurer de l'achat de parts entières
#     final_weights = adjust_for_whole_shares(opt_results.x, stock_prices, capital)
#
#     return final_weights
#
#
# def optimize_only_stocks(risk_tolerance, stocks_avg_daily_returns, stocks_volatility, rf_daily):
#     num_stocks = len(stocks_avg_daily_returns)
#
#     def negative_sharpe_ratio_stocks(weights):
#         # Utilisez les variables du contexte de perform_optimization
#         stocks_returns = stocks_avg_daily_returns
#         stocks_vol = stocks_volatility
#         rf_rate = rf_daily
#
#         if risk_tolerance == 'low':
#             adjusted_stocks_returns = stocks_returns * 0.5
#         elif risk_tolerance == 'medium':
#             adjusted_stocks_returns = stocks_returns * 0.75
#         elif risk_tolerance == 'high':
#             # Pour une tolérance au risque élevée, on ne modifie pas les rendements attendus
#             adjusted_stocks_returns = stocks_returns
#
#         portfolio_return = np.dot(weights, adjusted_stocks_returns)
#         portfolio_vol = np.sqrt(
#             np.dot(weights ** 2, stocks_vol ** 2))
#         sharpe_ratio = (portfolio_return - rf_rate) / portfolio_vol
#         return -sharpe_ratio
#
#     # Contraintes : La somme des poids doit être égale à 1
#     constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
#
#     # Bornes : Chaque poids doit être compris entre 0 et 1
#     bounds = tuple((0, 1) for _ in range(num_stocks))
#
#     # Point de départ pour l'optimisation : Répartition uniforme
#     init_guess = [1.0 / num_stocks] * num_stocks
#
#     # Exécution de l'optimisation
#     opt_results = minimize(
#         negative_sharpe_ratio_stocks, init_guess,
#         method='SLSQP', bounds=bounds, constraints=constraints
#     )
#
#     return opt_results.x
#
#
# def define_max_crypto_weight(score, investment_horizon):
#     if score <= 6:
#         max_crypto_weight = 0.0
#         risk_tolerance = "low"
#     elif 7 <= score <= 10:
#         max_crypto_weight = 0.2 if investment_horizon > 5 else 0.1
#         risk_tolerance = 'medium'
#     else:
#         max_crypto_weight = 0.5 if investment_horizon > 5 else 0.25
#         risk_tolerance = 'high'
#     return max_crypto_weight, risk_tolerance
#
#
# def optimize_portfolio(capital, max_crypto_weight, stocks_avg_daily_returns, stocks_volatility,
#                        crypto_avg_daily_returns, crypto_volatility, rf_daily, risk_tolerance):
#
#     eligible_crypto_indices = list(range(len(crypto_avg_daily_returns)))  # Utilisez les indices
#     optimal_allocation_found = False
#
#     while not optimal_allocation_found:
#         optimal_weights = perform_optimization(eligible_crypto_indices, risk_tolerance, max_crypto_weight,
#                                                stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns,
#                                                crypto_volatility, rf_daily)
#         stock_weights = optimal_weights[:len(stocks_avg_daily_returns)]
#         crypto_weights = optimal_weights[len(stocks_avg_daily_returns):]
#
#         crypto_investments = [weight * capital for weight in crypto_weights]
#         cryptos_to_remove = [i for i, investment in enumerate(crypto_investments) if investment < 10]
#
#         if not cryptos_to_remove:
#             optimal_allocation_found = True
#         else:
#             eligible_crypto_indices = [i for i in eligible_crypto_indices if i not in cryptos_to_remove]
#
#     return stock_weights, crypto_weights
#
#
# def perform_optimization(eligible_crypto_indices, risk_tolerance, max_crypto_weight, stocks_avg_daily_returns,
#                          stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily):
#     num_stocks = len(stocks_avg_daily_returns)
#     num_cryptos = len(eligible_crypto_indices)
#
#     def negative_sharpe_ratio(weights):
#         # Utilisez les variables du contexte de perform_optimization
#         stocks_returns = stocks_avg_daily_returns
#         stocks_vol = stocks_volatility
#         crypto_returns = crypto_avg_daily_returns[eligible_crypto_indices]
#         crypto_vol = crypto_volatility[eligible_crypto_indices]
#         rf_rate = rf_daily
#
#         if risk_tolerance == 'low':
#             adjusted_stocks_returns = stocks_returns * 0.5
#             adjusted_crypto_returns = crypto_returns * 0.5
#         elif risk_tolerance == 'medium':
#             adjusted_stocks_returns = stocks_returns * 0.75
#             adjusted_crypto_returns = crypto_returns * 0.75
#         elif risk_tolerance == 'high':
#             # Pour une tolérance au risque élevée, on ne modifie pas les rendements attendus
#             adjusted_stocks_returns = stocks_returns
#             adjusted_crypto_returns = crypto_returns
#
#         portfolio_return = np.dot(weights[:num_stocks], adjusted_stocks_returns) + np.dot(weights[num_stocks:],
#                                                                                           adjusted_crypto_returns)
#         portfolio_vol = np.sqrt(
#             np.dot(weights[:num_stocks] ** 2, stocks_vol ** 2) + np.dot(weights[num_stocks:] ** 2, crypto_vol ** 2))
#         sharpe_ratio = (portfolio_return - rf_rate) / portfolio_vol
#         return -sharpe_ratio
#
#     constraints = [
#         {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
#         {'type': 'ineq', 'fun': lambda x: max_crypto_weight - np.sum(x[num_stocks:])}
#     ]
#     bounds = tuple((0, 1) for _ in range(num_stocks + num_cryptos))
#     init_guess = [1.0 / (num_stocks + num_cryptos)] * (num_stocks + num_cryptos)
#
#     opt_results = minimize(
#         negative_sharpe_ratio, init_guess,
#         method='SLSQP', bounds=bounds, constraints=constraints
#     )
#
#     return opt_results.x

