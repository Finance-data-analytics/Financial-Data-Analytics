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



def recommend_portfolio(score, capital, investment_horizon, stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily,stocks_info,crypto_info):
    # Définition de la tolérance au risque basée sur le score
    max_crypto_weight = 0.0  # Initialisation à 0 pour le cas à faible risque
    if score <= 5:
        risk_tolerance = 'low'
    elif 6 <= score <= 10:
        risk_tolerance = 'medium'
        max_crypto_weight = 0.2 if investment_horizon > 5 else 0.1  # Poids plus faible si l'horizon est court
    else:
        risk_tolerance = 'high'
        max_crypto_weight = 0.5 if investment_horizon > 5 else 0.25  # Poids plus faible si l'horizon est court

    stock_prices = {}
    for identifier in stocks_info:
        data = yf.download(identifier, period="5d")
        stock_prices[identifier] = data['Adj Close'][-1] if not data.empty else None
    print(stock_prices)

    num_stocks = len(stocks_avg_daily_returns)
    num_cryptos = len(crypto_avg_daily_returns)

    # Fonction pour calculer le ratio de Sharpe négatif
    def negative_sharpe_ratio(weights, stocks_returns, stocks_vol, crypto_returns, crypto_vol, rf_rate):
        # Calcul des rendements et volatilité pondérés du portefeuille
        portfolio_return = np.dot(weights[:num_stocks], stocks_returns) + np.dot(weights[num_stocks:], crypto_returns)
        portfolio_vol = np.sqrt(np.dot(weights[:num_stocks]**2, stocks_vol**2) + np.dot(weights[num_stocks:]**2, crypto_vol**2))
        sharpe_ratio = (portfolio_return - rf_rate) / portfolio_vol
        return -sharpe_ratio  # Minimiser pour maximiser le ratio de Sharpe

    # Contraintes: la somme des poids est 1 et la pondération de la crypto ne dépasse pas le maximum autorisé
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Somme des poids = 1
        {'type': 'ineq', 'fun': lambda x: max_crypto_weight - np.sum(x[num_stocks:])},  # Poids crypto <= max_crypto_weight
        {'type': 'ineq', 'fun': lambda x: capital - np.dot(x, np.concatenate((np.ones(num_stocks) * capital, np.ones(num_cryptos) * (capital * max_crypto_weight))))}  # Contrainte de budget
    ]

    bounds = tuple((0, 1) for _ in range(num_stocks + num_cryptos))

    init_guess = [1.0 / (num_stocks + num_cryptos)] * (num_stocks + num_cryptos)

    opt_results = minimize(
        negative_sharpe_ratio, init_guess,
        args=(stocks_avg_daily_returns, stocks_volatility, crypto_avg_daily_returns, crypto_volatility, rf_daily),
        method='SLSQP', bounds=bounds, constraints=constraints
    )

    optimal_weights = opt_results.x
    stock_weights = optimal_weights[:num_stocks]
    crypto_weights = optimal_weights[num_stocks:]

    # Ajustement des poids pour respecter le capital total
    if np.sum(stock_weights) + np.sum(crypto_weights) > 1:
        total_weights = np.sum(stock_weights) + np.sum(crypto_weights)
        stock_weights = stock_weights / total_weights
        crypto_weights = crypto_weights / total_weights

    stock_investment = capital * stock_weights
    crypto_investment = capital * crypto_weights

    return stock_investment, crypto_investment





