import pandas as pd
import yfinance as yf
import concurrent.futures

def check_ticker(index, ticker):
    print(f"Checking line number: {index}")
    try:
        # Just grab the info, which is quicker than downloading historical data
        stock_info = yf.Ticker(ticker).info
        return ticker, True  # Return ticker and a status indicating success
    except:
        return ticker, False  # Return ticker and a status indicating failure

# Load the Excel file into a DataFrame
df = pd.read_excel('all_tickers.xlsx')

# Get the list of tickers from the first column of the DataFrame
tickers_to_check = df[df.columns[0]].tolist()

# A dictionary to store the results of parallel checks
results = {}

# Using ThreadPoolExecutor to parallelize the process
with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:  # You can adjust max_workers as needed
    future_to_ticker = {executor.submit(check_ticker, index+1, ticker): ticker for index, ticker in enumerate(tickers_to_check)}
    for future in concurrent.futures.as_completed(future_to_ticker):
        ticker = future_to_ticker[future]
        try:
            ticker, success = future.result()
            results[ticker] = success
        except Exception as e:
            print(f"Error with ticker {ticker}: {e}")
            results[ticker] = False

# Remove tickers that had errors
for ticker, success in results.items():
    if not success:
        df = df[df[df.columns[0]] != ticker]

# Save the modified DataFrame back to the Excel file
df.to_excel('all_tickers_good.xlsx', index=False)
import yfinance as yf
import numpy as np
import pandas as pd
import requests
from matplotlib import cm
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
    crypto_df['Symbol'] = crypto_df['Symbol'].apply(lambda x: x + '-USD')
    crypto_df.to_excel("cryptos_market_cap.xlsx", index=False)

def get_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data

def calculate_returns(data):
    returns = data.pct_change().dropna()
    return returns

def efficient_frontier(returns,target_return_):
    cov_matrix = returns.cov()
    avg_returns = returns.mean()

    num_assets = len(returns.columns)
    args = (avg_returns, cov_matrix)

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                   {'type': 'eq', 'fun': lambda x: np.sum(x * avg_returns) - target_return_})

    bounds = tuple((0, 1) for asset in range(num_assets))
    results = minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, constraints=constraints, bounds=bounds)
    return results

def portfolio_volatility(weights, avg_returns, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

get_crypto_data()
crypto_data = pd.read_excel("cryptos_market_cap.xlsx")
crypto_symbols = crypto_data['Symbol'].tolist()

all_stocks = pd.read_excel("all_tickers.xlsx")
first_100_stocks = all_stocks['Symbol'][:500].tolist()
first_100_stocks = [str(ticker) for ticker in first_100_stocks]

crypto_data = get_data(crypto_symbols, '2019-01-01', '2023-10-01')
stocks_data = get_data(first_100_stocks, '2019-01-01', '2023-10-01')

crypto_daily_returns = calculate_returns(crypto_data)
stocks_daily_returns = calculate_returns(stocks_data)

crypto_avg_daily_returns = crypto_daily_returns.mean()
stocks_avg_daily_returns = stocks_daily_returns.mean()

crypto_risks = crypto_daily_returns.std()
stocks_risks = stocks_daily_returns.std()

# # Créez un DataFrame pour stocker le rendement moyen et le risque de chaque action
# Create dictionary of results
results_dict = {
    "Stocks": pd.DataFrame({
        "Rendement moyen": stocks_avg_daily_returns,
        "Risque": stocks_risks
    }),
    "Crypto": pd.DataFrame({
        "Rendement moyen": crypto_avg_daily_returns,
        "Risque": crypto_risks
    })
}

# Use ExcelWriter to save these DataFrames into separate sheets of the same Excel file
with pd.ExcelWriter("rendements_et_risques.xlsx") as writer:
    for sheet_name, result in results_dict.items():
        result.to_excel(writer, sheet_name=sheet_name)
# # Pour différentes cibles de rendement, définir la target_return et trouver les poids optimaux
target_returns_stock = np.linspace(stocks_avg_daily_returns.min(), stocks_avg_daily_returns.max(), 100)
target_returns_crypto = np.linspace(crypto_avg_daily_returns.min(), crypto_avg_daily_returns.max(), 100)

# Dictionary containing average daily returns and daily returns for each asset type
data_dict = {
    "Stocks": (stocks_avg_daily_returns, stocks_daily_returns),
    "Crypto": (crypto_avg_daily_returns, crypto_daily_returns)
}

# Empty dictionary to store efficient portfolios for each asset type
efficient_portfolios_dict = {}

# Loop over the dictionary
for asset_type, (avg_daily_returns, daily_returns) in data_dict.items():
    target_returns = np.linspace(avg_daily_returns.min(), avg_daily_returns.max(), 100)
    efficient_portfolios = [efficient_frontier(daily_returns, target_return) for target_return in target_returns]
    efficient_portfolios_dict[asset_type] = efficient_portfolios

# Dictionary containing data for plotting
plotting_data = {
    "Cryptos": {
        "risks": crypto_risks,
        "avg_daily_returns": crypto_avg_daily_returns,
        "symbols": crypto_symbols,
        "efficient_portfolios": efficient_portfolios_dict["Crypto"],
        "color": 'b',
        "title": 'Cryptos: Rendement vs Risque'
    },
    "Stocks": {
        "risks": stocks_risks,
        "avg_daily_returns": stocks_avg_daily_returns,
        "symbols": first_100_stocks,
        "efficient_portfolios": efficient_portfolios_dict["Stocks"],
        "color": 'r',
        "title": 'Stocks: Rendement vs Risque'
    }
}

# Adjust the plotting function to use the daily risk-free rate

import plotly.graph_objects as go


def plot_assets_and_cal_plotly(data_dict, rf_daily):
    for key, data in data_dict.items():
        # Create a scatter plot for assets
        fig = go.Figure()

        # Plotting individual asset points with their names
        for ticker in data["symbols"]:
            if ticker == 'nan' or ticker == '':
                continue  # Skip this iteration if the ticker is 'nan' or an empty string

            fig.add_trace(go.Scatter(x=[data["risks"][ticker]],
                                     y=[data["avg_daily_returns"][ticker]],
                                     mode='markers',
                                     name=ticker))

            # Plotting the efficient frontier
        portfolio_volatilities = [portfolio['fun'] for portfolio in data["efficient_portfolios"]]
        target_returns = np.linspace(data["avg_daily_returns"].min(), data["avg_daily_returns"].max(), 100)
        fig.add_trace(go.Scatter(x=portfolio_volatilities, y=target_returns, mode='lines',
                                 name='Frontière Efficient de Markowitz', line=dict(color='yellow')))

        # Calculate the slope of the tangent for each portfolio on the efficient frontier
        slopes = [(np.dot(data["avg_daily_returns"], portfolio.x) - rf_daily) / portfolio.fun for portfolio in
                  data["efficient_portfolios"]]

        # Find the portfolio with the steepest slope
        max_slope_idx = np.argmax(slopes)
        tangent_portfolio = data["efficient_portfolios"][max_slope_idx]

        # Return and volatility of the tangent portfolio
        tangent_return = np.dot(data["avg_daily_returns"], tangent_portfolio.x)
        tangent_volatility = tangent_portfolio.fun

        # Plot the CAL
        x = np.linspace(0, max(portfolio_volatilities), 100)
        y = rf_daily + (tangent_return - rf_daily) / tangent_volatility * x
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='CAL', line=dict(color='green', dash='dash')))

        # Layout settings
        fig.update_layout(title=data["title"], xaxis_title='Volatilité (Écart type du rendement)',
                          yaxis_title='Rendement attendu')
        fig.show()


# Convert the annual risk-free rate to a daily rate
rf_annual = 0.01  # 1% annual rate
rf_daily = (1 + rf_annual)**(1/365) - 1
rf_daily

# Plot the assets and CAL using the daily risk-free rate
plot_assets_and_cal_plotly(plotting_data, rf_daily)

