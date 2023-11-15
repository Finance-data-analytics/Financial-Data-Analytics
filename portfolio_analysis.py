from config import *
from data_retrieval import *

def portfolio_volatility(weights, avg_returns, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def calculate_returns(data):
    returns = data.pct_change().dropna()
    return returns

def efficient_frontier(returns,target_return_,min_diversification=0):
    cov_matrix = returns.cov()
    avg_returns = returns.mean()

    num_assets = len(returns.columns)
    args = (avg_returns, cov_matrix)

    if min_diversification > 0:
        cons = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - min_diversification},)

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                   {'type': 'eq', 'fun': lambda x: np.sum(x * avg_returns) - target_return_})

    bounds = tuple((0, 1) for asset in range(num_assets))
    results = minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, constraints=constraints, bounds=bounds)
    return results




def recommend_portfolio(capital, investment_horizon, risk_tolerance, stocks_avg_daily_returns, crypto_avg_daily_returns):
    if investment_horizon <= 3:  # Short term
        target_return = stocks_avg_daily_returns.min()
    elif investment_horizon <= 7:  # Medium term
        target_return = stocks_avg_daily_returns.mean()
    else:  # Long term
        target_return = stocks_avg_daily_returns.max()

    if risk_tolerance == "faible":
        target_return -= 0.01
        max_crypto_weight = 0  # No crypto for low-risk profile
        min_stock_diversification = 0.8  # At least 80% diversification among stocks
    elif risk_tolerance == "moyenne":
        max_crypto_weight = 0.2  # Up to 20% crypto for medium-risk profile
        min_stock_diversification = 0.5  # At least 50% diversification among stocks
    else:  # élevée
        target_return += 0.01
        max_crypto_weight = 0.5  # Up to 50% crypto for high-risk profile
        min_stock_diversification = 0.2  # At least 20% diversification among stocks

    stock_portfolio = efficient_frontier(stocks_daily_returns, target_return, min_diversification=min_stock_diversification)['x']
    crypto_portfolio = efficient_frontier(crypto_daily_returns, target_return)['x']

    # Ensure we don't exceed the max_crypto_weight for the risk profile
    total_crypto_weight = np.sum(crypto_portfolio)
    if total_crypto_weight > max_crypto_weight:
        crypto_portfolio = (crypto_portfolio / total_crypto_weight) * max_crypto_weight

    # Remaining weight is for stocks
    total_stock_weight = 1 - total_crypto_weight

    total_stock_investment = capital * total_stock_weight
    total_crypto_investment = capital * total_crypto_weight
    
    stock_investment = stock_portfolio * total_stock_investment
    crypto_investment = crypto_portfolio * total_crypto_investment

    return stock_investment, crypto_investment

