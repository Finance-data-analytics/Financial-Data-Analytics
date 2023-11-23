from config import *


def calculate_individual_alpha_beta(combined_data, market_returns, ticker_to_isin):
    alphas = []
    betas = []

    asset_alphas, asset_beta = calculate_individual_alpha__and_beta(combined_data, market_returns, ticker_to_isin)
    betas.append(asset_beta)
    alphas.append(asset_alphas)

    return alphas, betas


def calculate_portfolio_beta_alpha(combined_data, market_returns, weights, ticker_to_isin):
    asset_alphas, asset_betas = calculate_individual_alpha__and_beta(combined_data, market_returns, ticker_to_isin)

    portfolio_beta = sum(w * beta for w, beta in zip(weights, asset_betas))
    portfolio_alpha = sum(w * alpha for w, alpha in zip(weights, asset_alphas))

    return portfolio_beta, portfolio_alpha


def calculate_individual_alpha__and_beta(combined_data, plotting_data, ticker_to_isin):
    asset_alphas = []
    asset_betas = []
    for stock in combined_data.columns:
        isin = ticker_to_isin.get(stock)
        if isin is None and "-USD" in stock:
            print(f"Crypto identified: {stock}")
            index_returns = plotting_data["Cryptos"]["daily_returns"]['BTC-USD']
          # Passez au ticker suivant si ISIN n'est pas trouvé
        elif isin is None:
            print(f"ISIN not found for ticker: {stock}")
            continue  # Passez au ticker suivant si ISIN n'est pas trouvé
        else:
            if isin.startswith("FR") or isin.startswith("LU") or isin.startswith("NL"):
                index_returns = plotting_data["Index"]["daily_returns"]['^FCHI']
            elif isin.startswith("DE"):
                index_returns = plotting_data["Index"]["daily_returns"]['^GDAXI']
            elif isin.startswith("US"):
                index_returns = plotting_data["Index"]["daily_returns"]['^DJI']
            elif isin.startswith("BE"):
                index_returns = plotting_data["Index"]["daily_returns"]['^BFX']
            elif isin.startswith("CH"):
                index_returns = plotting_data["Index"]["daily_returns"]['^SSMI']


        asset_beta = calculate_beta(combined_data[stock].ffill().pct_change(), index_returns)
        asset_alpha = calculate_alpha(combined_data[stock].pct_change().mean() * 252, asset_beta, index_returns.mean() * 252)
        asset_alphas.append(asset_alpha)
        asset_betas.append(asset_beta)

    return asset_betas, asset_betas


def calculate_beta(asset_returns, market_returns):


    # Maintenant, vous pouvez calculer la covariance et la variance
    covariance = asset_returns.cov(market_returns)
    variance = market_returns.var()

    # Calculer le beta
    beta = covariance / variance
    return beta



def calculate_alpha(asset_return, beta, market_return):
    alpha = asset_return - (beta * market_return)
    return alpha


def calculate_historical_return(data):
    """
    Calcule le rendement historique moyen d'un portefeuille.

    :param data: DataFrame contenant les prix historiques des actifs du portefeuille.
    :return: Rendement historique moyen annuel.
    """
    annual_returns = data.pct_change().mean() * 252  # 252 jours de trading dans une année
    historical_return = annual_returns.mean()
    return historical_return


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
    nb_crypto_ok = int(nb_stocks * crypto_limit)
    nb_stocks_ok = nb_stocks - nb_crypto_ok
    selection_results = []

    for _ in range(nb_simulations):
        historical_return = calculate_historical_return(stocks_data)
        selected_stocks = run_monte_carlo(stocks_data, 1, nb_stocks_ok, risk_profile, historical_return)

        if nb_crypto_ok > 0:
            historical_return = calculate_historical_return(crypto_data)
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
                           crypto_weight_limit, ticker_to_isin, index_data):
    combined_data = pd.concat([stocks_data[selected_stocks], crypto_data[selected_cryptos]], axis=1)
    best_sharpe_ratio = -np.inf
    best_weights = None

    # Initialisation des tableaux pour les retours, volatilités, ratios de Sharpe, bêtas et alphas
    ret_arr = np.zeros(nb_simulations)
    vol_arr = np.zeros(nb_simulations)
    sharpe_arr = np.zeros(nb_simulations)
    all_alphas = []
    all_betas = []

    for i in range(nb_simulations):
        weights = np.random.random(len(combined_data.columns))
        weights /= np.sum(weights)

        if sum(weights[len(selected_stocks):]) <= crypto_weight_limit:
            daily_returns = combined_data.ffill().pct_change().dropna().dot(weights)
            annual_return = daily_returns.mean() * 252
            annual_volatility = daily_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / annual_volatility

            ret_arr[i] = annual_return
            vol_arr[i] = annual_volatility
            sharpe_arr[i] = sharpe_ratio

            if sharpe_ratio > best_sharpe_ratio:
                best_sharpe_ratio = sharpe_ratio
                best_weights = weights

            # Calcul des alphas et bêtas pour chaque actif
    asset_alphas, asset_betas = calculate_individual_alpha_beta(combined_data, index_data,ticker_to_isin)
    all_alphas.append(asset_alphas)
    all_betas.append(asset_betas)
    best_portfolio_beta, best_portfolio_alpha = calculate_portfolio_beta_alpha(combined_data, index_data, weights,ticker_to_isin)
    return best_weights, ret_arr, vol_arr, sharpe_arr, all_alphas, all_betas, best_portfolio_beta, best_portfolio_alpha


def recommend_portfolio(nb_stocks, data_stock, data_crypto, capital,
                        portfolio_suggestion,
                        investment_horizon):
    crypto_weight_limit, risk_adjustment_factor = get_crypto_weight_limit(portfolio_suggestion, investment_horizon)

    # Drop any NaN values to clean the data
    stocks_data = data_stock.dropna()

    crypto_data = data_crypto.dropna()

    Top_5_Selection = monte_carlo_selection(
        stocks_data, crypto_data,
        1000,
        nb_stocks, crypto_weight_limit, risk_adjustment_factor)
    return crypto_weight_limit, stocks_data, crypto_data, capital, Top_5_Selection


def best_weigth(crypto_weight_limit, stocks_data, crypto_data, capital, selected_stocks,
                selected_cryptos, ticker_to_isin, index_data):
    best_weights, ret_arr_allocation, vol_arr_allocation, sharpe_arr_allocation, all_alphas, all_betas, best_portfolio_beta, best_portfolio_alpha = monte_carlo_allocation(
        stocks_data,
        crypto_data,
        selected_stocks,
        selected_cryptos
        , 1000,
        crypto_weight_limit, ticker_to_isin, index_data)
    monetary_allocation = best_weights * capital

    combined_selected_assets = selected_stocks + selected_cryptos
    print(all_alphas, all_betas, best_portfolio_beta, best_portfolio_alpha)
    return combined_selected_assets, monetary_allocation, best_weights, ret_arr_allocation, vol_arr_allocation, sharpe_arr_allocation, all_alphas, all_betas, best_portfolio_beta, best_portfolio_alpha


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
