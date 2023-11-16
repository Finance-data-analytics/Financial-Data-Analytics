from config import *
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

def recommend_portfolio(score, capital, investment_horizon, stocks_avg_daily_returns, crypto_avg_daily_returns, rf_daily):
    # Define the risk tolerance based on the score
    if score <= 5:
        risk_tolerance = 'low'
        max_crypto_weight = 0.0  # No crypto for low-risk profile
    elif 6 <= score <= 10:
        risk_tolerance = 'medium'
        max_crypto_weight = 0.2  # Up to 20% crypto for medium-risk profile
    else:
        risk_tolerance = 'high'
        max_crypto_weight = 0.5  # Up to 50% crypto for high-risk profile
    
    # Define target return based on risk tolerance and investment horizon
    if investment_horizon < 5:  # Short term
        target_return = stocks_avg_daily_returns.min()
    elif investment_horizon < 10:  # Medium term
        target_return = np.mean([stocks_avg_daily_returns.mean(), crypto_avg_daily_returns.mean()])
    else:  # Long term
        target_return = stocks_avg_daily_returns.max()

    # Optimization function for portfolio allocation
    def portfolio_volatility(weights, stocks_returns, crypto_returns):
        # Combine the stock and crypto returns
        portfolio_returns = np.dot(weights, np.concatenate([stocks_returns, crypto_returns]))
        return np.std(portfolio_returns)

    # Constraint: the sum of weights is 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Bounds for each asset in portfolio: 0% to 100%
    bounds = tuple((0, 1) for asset in range(len(stocks_avg_daily_returns) + len(crypto_avg_daily_returns)))
    
    # Initial guess for the weights (evenly distributed)
    init_guess = [1.0 / (len(stocks_avg_daily_returns) + len(crypto_avg_daily_returns))] * \
                 (len(stocks_avg_daily_returns) + len(crypto_avg_daily_returns))

    # Optimization to minimize volatility for the given target return
    opt_results = minimize(portfolio_volatility, init_guess, args=(stocks_avg_daily_returns, crypto_avg_daily_returns), 
                           method='SLSQP', constraints=constraints, bounds=bounds)

    # Extract the optimal weights for stocks and cryptos
    stock_weights = opt_results.x[:len(stocks_avg_daily_returns)]
    crypto_weights = opt_results.x[len(stocks_avg_daily_returns):]

    # Adjust crypto weights according to max allowed based on risk tolerance
    total_crypto_weight = np.sum(crypto_weights)
    if total_crypto_weight > max_crypto_weight:
        excess_weight = total_crypto_weight - max_crypto_weight
        # Scale down crypto weights
        crypto_weights = crypto_weights - (crypto_weights / total_crypto_weight * excess_weight)
        # Add the excess weight back to stocks
        stock_weights = stock_weights + (stock_weights / np.sum(stock_weights) * excess_weight)

    # Calculate the capital allocation
    stock_investment = capital * stock_weights
    crypto_investment = capital * crypto_weights

    return stock_investment, crypto_investment

