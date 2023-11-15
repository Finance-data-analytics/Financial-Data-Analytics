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

# def recommend_portfolio(capital, investment_horizon, risk_tolerance, stocks_avg_daily_returns, crypto_avg_daily_returns,stocks_daily_returns,crypto_daily_returns):
#     if investment_horizon <= 3:  # Short term
#         target_return = stocks_avg_daily_returns.min()
#     elif investment_horizon <= 7:  # Medium term
#         target_return = stocks_avg_daily_returns.mean()
#     else:  # Long term
#         target_return = stocks_avg_daily_returns.max()
#
#     if risk_tolerance == "faible":
#         target_return -= 0.01
#         max_crypto_weight = 0  # No crypto for low-risk profile
#         min_stock_diversification = 0.8  # At least 80% diversification among stocks
#     elif risk_tolerance == "moyenne":
#         max_crypto_weight = 0.2  # Up to 20% crypto for medium-risk profile
#         min_stock_diversification = 0.5  # At least 50% diversification among stocks
#     else:  # élevée
#         target_return += 0.01
#         max_crypto_weight = 0.5  # Up to 50% crypto for high-risk profile
#         min_stock_diversification = 0.2  # At least 20% diversification among stocks
#
#     stock_portfolio = efficient_frontier(stocks_daily_returns, target_return, min_diversification=min_stock_diversification)['x']
#     crypto_portfolio = efficient_frontier(crypto_daily_returns, target_return)['x']
#
#     # Ensure we don't exceed the max_crypto_weight for the risk profile
#     total_crypto_weight = np.sum(crypto_portfolio)
#     if total_crypto_weight > max_crypto_weight:
#         crypto_portfolio = (crypto_portfolio / total_crypto_weight) * max_crypto_weight
#
#     # Remaining weight is for stocks
#     total_stock_weight = 1 - total_crypto_weight
#
#     total_stock_investment = capital * total_stock_weight
#     total_crypto_investment = capital * total_crypto_weight
#
#     stock_investment = stock_portfolio * total_stock_investment
#     crypto_investment = crypto_portfolio * total_crypto_investment
#
#     return stock_investment, crypto_investment

