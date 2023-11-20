from config import *


def calculate_historical_return(data):
    """
    Calcule le rendement historique moyen d'un portefeuille.

    :param data: DataFrame contenant les prix historiques des actifs du portefeuille.
    :return: Rendement historique moyen annuel.
    """
    annual_returns = data.pct_change().mean() * 252  # 252 jours de trading dans une année
    historical_return = annual_returns.mean()
    return historical_return


def plot_top_selections(top_selections):
    plt.figure(figsize=(12, 8))

    for i, selection in enumerate(top_selections, start=1):
        plt.scatter(selection['volatility'], selection['return'], label=f'Top {i} (Score: {selection["score"]:.2f})')
        plt.text(selection['volatility'], selection['return'], f'{selection["stocks"]} | {selection["cryptos"]}')

    plt.xlabel('Volatility')
    plt.ylabel('Expected Return')
    plt.title('Top 5 Portfolio Selections')
    plt.legend()
    plt.show()


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


def is_portfolio_well_diversified(weights, threshold=0.15):
    """
    Évalue si le portefeuille est bien diversifié.

    :param weights: Poids des actifs dans le portefeuille.
    :param threshold: Seuil pour considérer un actif comme ayant un poids significatif.
    :return: True si le portefeuille est bien diversifié, False sinon.
    """
    significant_assets = [weight for weight in weights if weight >= threshold]
    return len(significant_assets) > 1  # Plus de 1 actif avec un poids significatif


def risk_penalty_function(volatility, risk_profile):
    # Appliquer une fonction de pénalité plus complexe basée sur la volatilité et le profil de risque
    # Cette fonction peut être ajustée pour être plus précise selon le profil
    risk_factors = {
        "No Crypto": 2,
        "Beginner": 1.5,
        "Very Conservative": 1.25,
        "Conservative": 1,
        "Balanced": 0.75,
        "Growth": 0.5,
        "Very Dynamic": 0.25
    }
    factor = risk_factors.get(risk_profile, 1)
    return volatility ** factor


def adjust_sharpe_ratio(sharpe_ratio, risk_profile, historical_return):
    # Ajuster le ratio de Sharpe pour refléter le profil de risque et le rendement historique
    adjustment = {
        "No Crypto": 0.8,
        "Beginner": 0.9,
        "Very Conservative": 0.95,
        "Conservative": 1,
        "Balanced": 1.05,
        "Growth": 1.1,
        "Very Dynamic": 1.2
    }
    sharpe_adjustment = adjustment.get(risk_profile, 1)
    return sharpe_ratio * sharpe_adjustment + historical_return * 0.1


def evaluate_portfolio_score(annual_return, annual_volatility, risk_profile, historical_return, weights):
    sharpe_ratio = annual_return / annual_volatility
    adjusted_sharpe = adjust_sharpe_ratio(sharpe_ratio, risk_profile, historical_return)
    volatility_penalty = risk_penalty_function(annual_volatility, risk_profile)

    # Déterminer si le portefeuille est bien diversifié à l'intérieur de la fonction
    well_diversified = is_portfolio_well_diversified(weights)
    diversification_bonus = 1.1 if well_diversified else 0.9

    final_score = (adjusted_sharpe / volatility_penalty) * diversification_bonus

    return final_score


# Function to perform Monte Carlo simulation for stock selection
def monte_carlo_selection(stocks_data, crypto_data, nb_simulations, nb_stocks, crypto_limit, risk_profile):
    print(risk_profile)
    nb_crypto_ok = int(nb_stocks * crypto_limit)
    nb_stocks_ok = nb_stocks - nb_crypto_ok

    selection_results = []

    for _ in range(nb_simulations):
        historical_return=calculate_historical_return(stocks_data)
        selected_stocks = run_monte_carlo(stocks_data, 1, nb_stocks_ok, risk_profile, historical_return)

        if nb_crypto_ok > 0:
            historical_return=calculate_historical_return(crypto_data)
            selected_cryptos = run_monte_carlo(crypto_data, 1, nb_crypto_ok, risk_profile, historical_return)
            combined_data = pd.concat([stocks_data[selected_stocks], crypto_data[selected_cryptos]], axis=1)
        else:
            selected_cryptos = []
            combined_data = stocks_data[selected_stocks]

        ret_arr, vol_arr, sharpe_arr, scores = run_full_monte_carlo(combined_data, 1, risk_profile, historical_return)

        selection_results.append({
            "stocks": selected_stocks,
            "cryptos": selected_cryptos,
            "return": ret_arr[0],
            "volatility": vol_arr[0],
            "sharpe_ratio": sharpe_arr[0],
            "score": scores[0]
        })

    # Trier les résultats en fonction du score et sélectionner les cinq premiers
    top_five_selections = sorted(selection_results, key=lambda x: x['score'], reverse=True)[:5]
    plot_top_selections(top_five_selections)
    return top_five_selections


def run_monte_carlo(data, nb_simulations, nb_selected, risk_profile, historical_return):
    best_score = -np.inf
    best_weights = None

    for _ in range(nb_simulations):
        weights = np.random.random(len(data.columns))
        weights /= np.sum(weights)

        daily_returns = data.pct_change().dropna().dot(weights)
        annual_return = daily_returns.mean() * 252
        annual_volatility = daily_returns.std() * np.sqrt(252)

        score = evaluate_portfolio_score(annual_return, annual_volatility, risk_profile, historical_return, weights)

        if score > best_score:
            best_score = score
            best_weights = weights

    # Sélectionner les actifs en fonction des meilleurs poids
    best_indices = np.argsort(-best_weights)[:nb_selected]
    selected_assets = data.columns[best_indices]

    return selected_assets


def run_full_monte_carlo(data, nb_simulations, risk_profile, historical_return):
    all_ret_arr = np.zeros(nb_simulations)
    all_vol_arr = np.zeros(nb_simulations)
    all_sharpe_arr = np.zeros(nb_simulations)
    all_scores = np.zeros(nb_simulations)

    for i in range(nb_simulations):
        weights = np.random.random(len(data.columns))
        weights /= np.sum(weights)

        # First, forward-fill any missing values
        data_ffilled = data.ffill()

        # Then, compute the percentage change
        daily_returns = data_ffilled.pct_change().dropna().dot(weights)

        annual_return = daily_returns.mean() * 252
        annual_volatility = daily_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility

        score = evaluate_portfolio_score(annual_return, annual_volatility, risk_profile, historical_return, weights)

        all_ret_arr[i] = annual_return
        all_vol_arr[i] = annual_volatility
        all_sharpe_arr[i] = sharpe_ratio
        all_scores[i] = score

    return all_ret_arr, all_vol_arr, all_sharpe_arr, all_scores


# Function to perform Monte Carlo simulation for weight allocation in the selected stocks
def monte_carlo_allocation(stocks_data, crypto_data, selected_stocks, selected_cryptos, nb_simulations,
                           crypto_weight_limit):
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


def get_portfolio_by_input(data):
    # Prompt the user to choose a portfolio
    print("Which portfolio do you want? Enter a number from 1 to 5:")
    user_input = input()

    # Check the user's input and provide the corresponding portfolio
    if user_input.isdigit():
        index = int(user_input) - 1  # Adjust for 0-based indexing
        if 0 <= index < len(data):
            portfolio = data[index]
            print("Portfolio", user_input, "selected.")

            # Extract stock and crypto indices into separate lists
            selected_stocks = portfolio['stocks']
            selected_cryptos = portfolio['cryptos']

            return selected_stocks, selected_cryptos
        else:
            print("Invalid input. Please enter a number between 1 and 5.")
    else:
        print("Invalid input. Please enter a valid number.")


def recommend_portfolio(nb_stocks, data_stock, data_crypto, capital,
                        portfolio_suggestion,
                        investment_horizon):
    crypto_weight_limit, risk_adjustment_factor = get_crypto_weight_limit(portfolio_suggestion, investment_horizon)

    # Drop any NaN values to clean the data
    stocks_data = data_stock.dropna()

    crypto_data = data_crypto.dropna()

    Top_5_Selection = monte_carlo_selection(
        stocks_data, crypto_data,
        10000,
        nb_stocks, crypto_weight_limit, risk_adjustment_factor)

    selected_stocks,selected_cryptos=get_portfolio_by_input(Top_5_Selection)    # Run the second Monte Carlo simulation for weight allocation
    best_weights, ret_arr_allocation, vol_arr_allocation, sharpe_arr_allocation = monte_carlo_allocation(stocks_data,
                                                                                                         crypto_data,
                                                                                                         selected_stocks,
                                                                                                         selected_cryptos
                                                                                                         , 10000,
                                                                                                         crypto_weight_limit)
    monetary_allocation = best_weights * capital
    # Création d'une liste combinée des actifs sélectionnés
    combined_selected_assets = selected_stocks.append(selected_cryptos)

    return combined_selected_assets,monetary_allocation,best_weights
    # print(best_weights)
    # print(combined_selected_assets)
    # print(monetary_allocation)
    # # Print the monetary allocation for the selected stocks and cryptos
    # print("Monetary allocation and Weights for the Best Portfolio:")
    # for asset, (allocation, weight) in zip(combined_selected_assets, zip(monetary_allocation, best_weights)):
    #     print(f"{asset}: ${allocation:,.2f} ({weight:.2%})")
    #
    # # Plot the results of the second Monte Carlo simulation
    # plt.figure(figsize=(12, 8))
    # plt.scatter(vol_arr_allocation, ret_arr_allocation, c=sharpe_arr_allocation, cmap='plasma')
    # plt.colorbar(label='Sharpe Ratio')
    # plt.xlabel('Volatility')
    # plt.ylabel('Return')
    # plt.title('Optimal Weight Allocation for Selected Stocks')
    #
    # # Highlight the best portfolio with a red dot
    # max_sharpe_idx = sharpe_arr_allocation.argmax()  # Index of the portfolio with the highest Sharpe Ratio
    # plt.scatter(vol_arr_allocation[max_sharpe_idx], ret_arr_allocation[max_sharpe_idx], c='red', s=50,
    #             edgecolors='black', label='Best Portfolio')
    #
    # # Show plot with legend
    # plt.legend()
    # plt.show()


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
        "Beginner": 0.025,
        "Very Conservative": 0.05,  # Très faible exposition aux cryptomonnaies
        "Conservative": 0.10,  # Faible exposition
        "Balanced": 0.15,  # Exposition modérée
        "Growth": 0.20,  # Exposition relativement plus élevée
        "Very Dynamic": 0.25  # Exposition agressive
    }.get(portfolio_suggestion, 0.10)  # Valeur par défaut si non spécifié
    risk_adjustment_factor = {
        "No Crypto": 2,
        "Beginner": 1.5,
        "Very Conservative": 1.75,
        "Conservative": 1.25,
        "Balanced": 1,
        "Growth": 0.75,
        "Very Dynamic": 0.5
    }.get(portfolio_suggestion, 1)  # Valeur par défaut si non spécifié

    # Ajustement en fonction de l'horizon d'investissement
    adjustment_factor = 1.0 + (0.1 * (investment_horizon // 5))  # Augmente de 10% tous les 5 ans

    # Calcul du poids limite ajusté
    adjusted_crypto_weight = base_crypto_weight * adjustment_factor

    # Assurer que le poids ne dépasse pas une certaine limite (par exemple, 40%)
    max_crypto_weight = 0.40
    return min(adjusted_crypto_weight, max_crypto_weight), risk_adjustment_factor

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