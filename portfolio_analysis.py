from config import *


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


def portfolio_volatility(weights, avg_returns, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


# Function to perform Monte Carlo simulation for stock selection
def monte_carlo_selection(stocks_data, crypto_data, nb_simulations, nb_stocks, crypto_limit):
    nb_crypto_ok = int(nb_stocks * crypto_limit)
    nb_stocks_ok = nb_stocks - nb_crypto_ok

    # Séparation des données en actions et cryptomonnaies
    stocks_only_data = stocks_data

    # Sélection des actions
    selected_stocks = run_monte_carlo(stocks_only_data, nb_simulations, nb_stocks_ok)
    if nb_crypto_ok == 0:
        selected_cryptos=[]
        combined_selected_data = stocks_data[selected_stocks]
    # Sélection des cryptomonnaies
    else:
        crypto_only_data = crypto_data
        selected_cryptos = run_monte_carlo(crypto_only_data, nb_simulations, nb_crypto_ok)
        # Combiner les actions et cryptomonnaies sélectionnées pour une analyse complète
        combined_selected_data = pd.concat([stocks_only_data[selected_stocks], crypto_only_data[selected_cryptos]], axis=1)
    ret_arr, vol_arr, sharpe_arr = run_full_monte_carlo(combined_selected_data, nb_simulations)

    return selected_stocks, selected_cryptos, ret_arr, vol_arr, sharpe_arr


def run_monte_carlo(data, nb_simulations, nb_selected):
    best_sharpe_ratio = -np.inf
    for i in range(nb_simulations):
        weights = np.random.random(len(data.columns))
        weights /= np.sum(weights)

        # Calcul des retours et de la volatilité
        daily_returns = (data.pct_change().dropna()).dot(weights)
        annual_return = daily_returns.mean() * 252
        annual_volatility = daily_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility

        if sharpe_ratio > best_sharpe_ratio:
            best_sharpe_ratio = sharpe_ratio
            best_weights = weights

    # Sélection des indices des meilleurs actifs
    best_indices = best_weights.argsort()[-nb_selected:]
    selected_assets = data.columns[best_indices]

    return selected_assets


def run_full_monte_carlo(data, nb_simulations):
    all_ret_arr = np.zeros(nb_simulations)
    all_vol_arr = np.zeros(nb_simulations)
    all_sharpe_arr = np.zeros(nb_simulations)

    for i in range(nb_simulations):
        weights = np.random.random(len(data.columns))
        weights /= np.sum(weights)

        # Calcul des retours et de la volatilité pour les données combinées
        daily_returns = (data.pct_change().dropna()).dot(weights)
        annual_return = daily_returns.mean() * 252
        annual_volatility = daily_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility

        all_ret_arr[i] = annual_return
        all_vol_arr[i] = annual_volatility
        all_sharpe_arr[i] = sharpe_ratio

    return all_ret_arr, all_vol_arr, all_sharpe_arr


# Function to perform Monte Carlo simulation for weight allocation in the selected stocks
def monte_carlo_allocation(stocks_data, crypto_data, selected_stocks, selected_cryptos, nb_simulations, crypto_weight_limit):
    # Filtrer les données pour ne garder que les actifs sélectionnés
    filtered_stock_data = stocks_data[selected_stocks]
    filtered_crypto_data = crypto_data[selected_cryptos]

    # Combinaison des données filtrées
    combined_data = pd.concat([filtered_stock_data, filtered_crypto_data], axis=1)

    best_sharpe_ratio = -np.inf
    best_weights = None

    # Initialisation des tableaux pour les retours, volatilités et ratios de Sharpe
    ret_arr = np.zeros(nb_simulations)
    vol_arr = np.zeros(nb_simulations)
    sharpe_arr = np.zeros(nb_simulations)

    for i in range(nb_simulations):
        weights = np.random.random(len(combined_data.columns))
        weights /= np.sum(weights)

        # Vérifier la limite pour les cryptomonnaies
        if sum(weights[len(filtered_stock_data.columns):]) <= crypto_weight_limit:
            # Calculer le rendement et la volatilité du portefeuille
            daily_returns = combined_data.ffill().pct_change().dropna().dot(weights)
            annual_return = daily_returns.mean() * 252
            annual_volatility = daily_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / annual_volatility

            # Stocker les résultats de chaque simulation
            ret_arr[i] = annual_return
            vol_arr[i] = annual_volatility
            sharpe_arr[i] = sharpe_ratio

            if sharpe_ratio > best_sharpe_ratio:
                best_sharpe_ratio = sharpe_ratio
                best_weights = weights

    return best_weights, ret_arr, vol_arr, sharpe_arr


def recommend_portfolio(nb_stocks, data_stock, data_crypto, capital,
                        portfolio_suggestion,
                        investment_horizon):
    crypto_weight_limit = get_crypto_weight_limit(portfolio_suggestion, investment_horizon)

    # Drop any NaN values to clean the data
    stocks_data = data_stock.dropna()

    crypto_data = data_crypto.dropna()

    selected_stocks, selected_cryptos, ret_arr_selection, vol_arr_selection, sharpe_arr_selection = monte_carlo_selection(
        stocks_data, crypto_data,
        10000,
        nb_stocks, crypto_weight_limit)

    # Run the second Monte Carlo simulation for weight allocation
    best_weights, ret_arr_allocation, vol_arr_allocation, sharpe_arr_allocation = monte_carlo_allocation(stocks_data,
                                                                                                         crypto_data,
                                                                                                         selected_stocks,
                                                                                                         selected_cryptos
                                                                                                         , 10000,
                                                                                                         crypto_weight_limit)
    monetary_allocation = best_weights * capital
    # Création d'une liste combinée des actifs sélectionnés

    combined_selected_assets = selected_stocks.append(selected_cryptos)

    # Print the monetary allocation for the selected stocks and cryptos
    print("Monetary allocation and Weights for the Best Portfolio:")
    for asset, (allocation, weight) in zip(combined_selected_assets, zip(monetary_allocation, best_weights)):
        print(f"{asset}: ${allocation:,.2f} ({weight:.2%})")

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


def get_crypto_weight_limit(portfolio_suggestion, investment_horizon):
    """
    Détermine le poids limite des cryptomonnaies dans le portefeuille en fonction de la suggestion de portefeuille et de l'horizon d'investissement.

    :param portfolio_suggestion: Suggestion de portefeuille (basée sur le score de risque).
    :param investment_horizon: Horizon d'investissement en années.
    :return: Le poids limite des cryptomonnaies dans le portefeuille.
    """

    # Poids de base pour les cryptomonnaies en fonction de la suggestion de portefeuille
    base_crypto_weight = {
        "No Crypto": 0,
        "Beginner":0.025,
        "Very Conservative": 0.05,  # Très faible exposition aux cryptomonnaies
        "Conservative": 0.10,  # Faible exposition
        "Balanced": 0.15,  # Exposition modérée
        "Growth": 0.20,  # Exposition relativement plus élevée
        "Very Dynamic": 0.25  # Exposition agressive
    }.get(portfolio_suggestion, 0.10)  # Valeur par défaut si non spécifié

    # Ajustement en fonction de l'horizon d'investissement
    adjustment_factor = 1.0 + (0.1 * (investment_horizon // 5))  # Augmente de 10% tous les 5 ans

    # Calcul du poids limite ajusté
    adjusted_crypto_weight = base_crypto_weight * adjustment_factor

    # Assurer que le poids ne dépasse pas une certaine limite (par exemple, 40%)
    max_crypto_weight = 0.40
    return min(adjusted_crypto_weight, max_crypto_weight)

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