import yfinance as yf
import numpy as np
import pandas as pd
import requests
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def get_crypto_data():
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '8ec7c7d5-f5ee-44a7-9d90-99ea1fb90edf',
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=15'
    response = requests.get(url, headers=headers)
    data = response.json()
    cryptos = data['data']

    crypto_data = []
    for crypto in cryptos:
        name = crypto['name']
        symbol = crypto['symbol']
        market_cap = crypto['quote']['USD']['market_cap']
        crypto_data.append({"Name": name, "Symbol": symbol, "Market Cap": market_cap})

    crypto_df = pd.DataFrame(crypto_data)
    print("Before modification:")
    print(crypto_df.head())
    
    crypto_df['Symbol'] = crypto_df['Symbol'].apply(lambda x: x + '-USD')
    
    print("\nAfter modification:")
    print(crypto_df.head())

    crypto_df.to_excel("cryptos_market_cap.xlsx", index=False)

# Lisez le fichier Excel contenant les cryptos
crypto_data = pd.read_excel("cryptos_market_cap.xlsx")

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

# Récupérer les données des cryptomonnaies
get_crypto_data()

# Lisez le fichier Excel contenant les cryptos
crypto_data = pd.read_excel("cryptos_market_cap.xlsx")

# Obtenez la liste des symboles des cryptos
crypto_symbols = crypto_data['Symbol'].tolist()

# Récupérer les données des actions
# Assuming the tickers are in a column named 'Ticker' in the all_tickers.xlsx file
all_stocks = pd.read_excel("all_tickers.xlsx")
first_100_stocks = all_stocks['Symbol'][:10].tolist()

tickers = []
tickers.extend(first_100_stocks)
tickers.extend(crypto_symbols)  # Ajout des symboles des cryptos à la liste tickers

data = get_data(tickers, '2015-01-01', '2023-10-01')

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

# Existing plotting code for efficient frontier
plt.plot(portfolio_volatilities, target_returns, 'y-', label='Frontière Efficient de Markowitz')

# New code to plot individual asset points without names
for i, ticker in enumerate(tickers):
    plt.scatter(risks[ticker], avg_daily_returns[ticker], marker='o', s=20)  # s=20 sets a smaller size for the scatter points

plt.xlabel('Volatilité (Écart type du rendement)')
plt.ylabel('Rendement attendu')
plt.legend()
plt.title('Frontière Efficient de Markowitz')
plt.grid(True)  # This will add gridlines for better readability
plt.show()
