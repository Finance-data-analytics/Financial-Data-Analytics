import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def get_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data

def calculate_returns(data):
    returns = data.pct_change().dropna()
    return returns

def efficient_frontier(returns):
    cov_matrix = returns.cov()
    avg_returns = returns.mean()

    num_assets = len(returns.columns)
    args = (avg_returns, cov_matrix)
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                   {'type': 'eq', 'fun': lambda x: np.sum(x * avg_returns) - target_return})
    
    bounds = tuple((0, 1) for asset in range(num_assets))
    
    results = minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, constraints=constraints, bounds=bounds)
    
    return results

def portfolio_volatility(weights, avg_returns, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

# Récupérer les données
tickers = ['AAPL', 'GOOGL', 'MSFT']
data = get_data(tickers, '2020-01-01', '2022-01-01')

# Calculer les rendements quotidiens
daily_returns = calculate_returns(data)

# Calculez le rendement moyen et l'écart type pour chaque action
avg_daily_returns = daily_returns.mean()
risks = daily_returns.std()

# Créez un DataFrame pour stocker le rendement moyen et le risque de chaque action
results = pd.DataFrame({
    "Rendement moyen": avg_daily_returns,
    "Risque": risks
})

# Sauvegardez ces résultats dans un fichier Excel
results.to_excel("rendements_et_risques.xlsx")

# Pour différentes cibles de rendement, définir la target_return et trouver les poids optimaux
target_returns = np.linspace(daily_returns.min().min(), daily_returns.max().max(), 100)
efficient_portfolios = []
for target_return in target_returns:
    efficient_portfolios.append(efficient_frontier(daily_returns))

portfolio_volatilities = [portfolio['fun'] for portfolio in efficient_portfolios]

# Tracez la frontière efficace de Markowitz
plt.plot(portfolio_volatilities, target_returns, 'y-', label='Frontière Efficient de Markowitz')
plt.xlabel('Volatilité (Écart type du rendement)')
plt.ylabel('Rendement attendu')
plt.legend()
plt.title('Frontière Efficient de Markowitz')
plt.show()
