from data_retrieval import *


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
    results = minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', constraints=constraints, bounds=bounds)
    return results


def recommend_portfolio(score, capital, investment_horizon, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily, stocks_info, crypto_info):
    max_crypto_weight, risk_tolerance = define_max_crypto_weight(score, investment_horizon)

    # Récupération des prix des stocks
    #stock_prices = {identifier: yf.download(identifier, period="5d")['Adj Close'].iloc[-1] for identifier in stocks_info}


    # Optimisation initiale du portefeuille
    stock_weights, crypto_weights = optimize_portfolio(capital, max_crypto_weight, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily, risk_tolerance)

    if not any(crypto_weight > 0 for crypto_weight in crypto_weights):
        stock_weights = optimize_only_stocks(risk_tolerance, stocks_avg_daily_returns, stocks_volatility, rf_daily)
    # Ajustement pour les parts entières et calcul du capital restant
    #stock_weights, remaining_capital = adjust_for_whole_shares(stock_weights, stock_prices, capital)

    # Calcul des investissements finaux
    stock_investment = np.array(stock_weights) * capital
    crypto_investment = np.array(crypto_weights) * capital

    return stock_investment, crypto_investment


def adjust_for_whole_shares(stock_weights, stock_prices, capital):
    adjusted_weights = []
    used_capital = 0
    for i, identifier in enumerate(stock_prices.keys()):
        stock_amount = stock_weights[i] * capital
        stock_price = stock_prices[identifier]
        num_shares = int(stock_amount / stock_price)
        adjusted_weight = num_shares * stock_price
        adjusted_weights.append(adjusted_weight / capital)
        used_capital += adjusted_weight
    remaining_capital = capital - used_capital
    return adjusted_weights, remaining_capital


def reoptimize_portfolio(current_weights, stock_prices, capital, stocks_avg_daily_returns, stocks_volatility, rf_daily, risk_tolerance):
    remaining_capital = capital - sum(weight * capital for weight in current_weights)
    num_stocks = len(stocks_avg_daily_returns)

    def negative_sharpe_ratio(weights):
        # Utilisez les variables du contexte pour calculer le ratio de Sharpe négatif
        portfolio_return = np.dot(weights, stocks_avg_daily_returns)
        portfolio_vol = np.sqrt(np.dot(weights ** 2, stocks_volatility ** 2))
        sharpe_ratio = (portfolio_return - rf_daily) / portfolio_vol
        return -sharpe_ratio

    # Contraintes pour garantir que la somme des poids est égale au capital restant
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - remaining_capital / capital},
        # Autres contraintes basées sur la tolérance au risque
    ]

    # Bornes pour chaque action
    bounds = [(0, 1) for _ in range(num_stocks)]

    # Initialisation des poids pour la réoptimisation
    init_guess = [(weight * capital + remaining_capital / num_stocks) / capital for weight in current_weights]

    # Exécution de l'optimisation avec les nouvelles contraintes
    opt_results = minimize(
        negative_sharpe_ratio, init_guess,
        method='SLSQP', bounds=bounds, constraints=constraints
    )

    # Ajustement final pour s'assurer de l'achat de parts entières
    final_weights = adjust_for_whole_shares(opt_results.x, stock_prices, capital)

    return final_weights


def optimize_only_stocks(risk_tolerance, stocks_avg_daily_returns, stocks_volatility, rf_daily):
    num_stocks = len(stocks_avg_daily_returns)

    def negative_sharpe_ratio_stocks(weights):
        # Utilisez les variables du contexte de perform_optimization
        stocks_returns = stocks_avg_daily_returns
        stocks_vol = stocks_volatility
        rf_rate = rf_daily

        if risk_tolerance == 'low':
            adjusted_stocks_returns = stocks_returns * 0.5
        elif risk_tolerance == 'medium':
            adjusted_stocks_returns = stocks_returns * 0.75
        elif risk_tolerance == 'high':
            # Pour une tolérance au risque élevée, on ne modifie pas les rendements attendus
            adjusted_stocks_returns = stocks_returns

        portfolio_return = np.dot(weights, adjusted_stocks_returns)
        portfolio_vol = np.sqrt(
            np.dot(weights ** 2, stocks_vol ** 2))
        sharpe_ratio = (portfolio_return - rf_rate) / portfolio_vol
        return -sharpe_ratio

    # Contraintes : La somme des poids doit être égale à 1
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

    # Bornes : Chaque poids doit être compris entre 0 et 1
    bounds = tuple((0, 1) for _ in range(num_stocks))

    # Point de départ pour l'optimisation : Répartition uniforme
    init_guess = [1.0 / num_stocks] * num_stocks

    # Exécution de l'optimisation
    opt_results = minimize(
        negative_sharpe_ratio_stocks, init_guess,
        method='SLSQP', bounds=bounds, constraints=constraints
    )

    return opt_results.x


def define_max_crypto_weight(score, investment_horizon):
    if score <= 6:
        max_crypto_weight = 0.0
        risk_tolerance="low"
    elif 7 <= score <= 10:
        max_crypto_weight = 0.2 if investment_horizon > 5 else 0.1
        risk_tolerance = 'medium'
    else:
        max_crypto_weight = 0.5 if investment_horizon > 5 else 0.25
        risk_tolerance = 'high'
    return max_crypto_weight,risk_tolerance


def optimize_portfolio(capital, max_crypto_weight, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily,risk_tolerance):
    eligible_crypto_indices = list(range(len(crypto_avg_daily_returns)))  # Utilisez les indices
    optimal_allocation_found = False

    while not optimal_allocation_found:
        optimal_weights = perform_optimization(eligible_crypto_indices, risk_tolerance, max_crypto_weight, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily)
        stock_weights = optimal_weights[:len(stocks_avg_daily_returns)]
        crypto_weights = optimal_weights[len(stocks_avg_daily_returns):]

        crypto_investments = [weight * capital for weight in crypto_weights]
        cryptos_to_remove = [i for i, investment in enumerate(crypto_investments) if investment < 10]

        if not cryptos_to_remove:
            optimal_allocation_found = True
        else:
            eligible_crypto_indices = [i for i in eligible_crypto_indices if i not in cryptos_to_remove]

    return stock_weights, crypto_weights


def perform_optimization(eligible_crypto_indices, risk_tolerance, max_crypto_weight, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily):
    num_stocks = len(stocks_avg_daily_returns)
    num_cryptos = len(eligible_crypto_indices)

    def negative_sharpe_ratio(weights):
        # Utilisez les variables du contexte de perform_optimization
        stocks_returns = stocks_avg_daily_returns
        stocks_vol = stocks_volatility
        crypto_returns = crypto_avg_daily_returns[eligible_crypto_indices]
        crypto_vol = crypto_volatility[eligible_crypto_indices]
        rf_rate = rf_daily

        if risk_tolerance == 'low':
            adjusted_stocks_returns = stocks_returns * 0.5
            adjusted_crypto_returns = crypto_returns * 0.5
        elif risk_tolerance == 'medium':
            adjusted_stocks_returns = stocks_returns * 0.75
            adjusted_crypto_returns = crypto_returns * 0.75
        elif risk_tolerance == 'high':
            # Pour une tolérance au risque élevée, on ne modifie pas les rendements attendus
            adjusted_stocks_returns = stocks_returns
            adjusted_crypto_returns = crypto_returns

        portfolio_return = np.dot(weights[:num_stocks], adjusted_stocks_returns) + np.dot(weights[num_stocks:],
                                                                                          adjusted_crypto_returns)
        portfolio_vol = np.sqrt(
            np.dot(weights[:num_stocks] ** 2, stocks_vol ** 2) + np.dot(weights[num_stocks:] ** 2, crypto_vol ** 2))
        sharpe_ratio = (portfolio_return - rf_rate) / portfolio_vol
        return -sharpe_ratio

    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'ineq', 'fun': lambda x: max_crypto_weight - np.sum(x[num_stocks:])}
    ]
    bounds = tuple((0, 1) for _ in range(num_stocks + num_cryptos))
    init_guess = [1.0 / (num_stocks + num_cryptos)] * (num_stocks + num_cryptos)

    opt_results = minimize(
        negative_sharpe_ratio, init_guess,
        method='SLSQP', bounds=bounds, constraints=constraints
    )

    return opt_results.x










