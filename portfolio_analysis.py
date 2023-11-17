from config import *
from data_retrieval import *
from scipy.optimize import minimize


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
    # Définition de la tolérance au risque et du poids maximum en crypto
    if score <= 6:
        risk_tolerance = 'low'
        max_crypto_weight = 0.0  # Aucune allocation en crypto pour un risque faible
    elif 7 <= score <= 10:
        risk_tolerance = 'medium'
        max_crypto_weight = 0.2 if investment_horizon > 5 else 0.1
    else:
        risk_tolerance = 'high'
        max_crypto_weight = 0.5 if investment_horizon > 5 else 0.25

    # Téléchargement des données des stocks
    #stock_prices = {identifier: yf.download(identifier, period="5d")['Adj Close'][-1] for identifier in stocks_info}

    num_stocks = len(stocks_avg_daily_returns)
    num_cryptos = len(crypto_avg_daily_returns)

    # Fonction pour calculer le ratio de Sharpe négatif
    def negative_sharpe_ratio(weights, risk_tolerance, stocks_returns, stocks_vol, crypto_returns, crypto_vol, rf_rate):
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

            # Calcul des rendements et volatilité pondérés du portefeuille
        portfolio_return = np.dot(weights[:num_stocks], adjusted_stocks_returns) + np.dot(weights[num_stocks:],
                                                                                          adjusted_crypto_returns)
        portfolio_vol = np.sqrt(
            np.dot(weights[:num_stocks] ** 2, stocks_vol ** 2) + np.dot(weights[num_stocks:] ** 2, crypto_vol ** 2))
        sharpe_ratio = (portfolio_return - rf_rate) / portfolio_vol
        return -sharpe_ratio

    # Contraintes et bornes
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'ineq', 'fun': lambda x: max_crypto_weight - np.sum(x[num_stocks:])}
    ]
    bounds = tuple((0, 1) for _ in range(num_stocks + num_cryptos))

    # Point de départ pour l'optimisation
    init_guess = [1.0 / (num_stocks + num_cryptos)] * (num_stocks + num_cryptos)

    # Optimisation
    opt_results = minimize(
        negative_sharpe_ratio, init_guess,
        args=(risk_tolerance, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily),
        method='SLSQP', bounds=bounds, constraints=constraints
    )

    # Récupération des poids optimaux
    optimal_weights = opt_results.x
    stock_weights = optimal_weights[:num_stocks]
    crypto_weights = optimal_weights[num_stocks:]

    # Calcul de l'allocation d'investissement
    stock_investment = capital * stock_weights
    crypto_investment = capital * crypto_weights

    return stock_investment, crypto_investment





