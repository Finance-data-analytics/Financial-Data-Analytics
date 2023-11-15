from config import *
from portfolio_analysis import calculate_returns, efficient_frontier


def get_crypto_data():
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '8ec7c7d5-f5ee-44a7-9d90-99ea1fb90edf',
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=30'
    response = requests.get(url, headers=headers)
    data = response.json()
    cryptos = data['data']

    # Liste des symboles des stablecoins à exclure
    stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'PAX', 'USDP', 'UNI']

    crypto_data = []
    for crypto in cryptos:
        name = crypto['name']
        symbol = crypto['symbol']
        # Excluez les cryptos si elles sont dans la liste des stablecoins
        if symbol not in stablecoins:
            market_cap = crypto['quote']['USD']['market_cap']
            crypto_data.append({"Name": name, "Symbol": symbol, "Market Cap": market_cap})

    crypto_df = pd.DataFrame(crypto_data)
    crypto_df['Symbol'] = crypto_df['Symbol'].apply(lambda x: x + '-USD')
    crypto_df.to_excel("cryptos_market_cap.xlsx", index=False)


get_crypto_data()
crypto_data = pd.read_excel("cryptos_market_cap.xlsx")
crypto_symbols = crypto_data['Symbol'].tolist()


def get_data(tickers, start_date, end_date):
    try:
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        return data
    except Exception as e:
        print(f"Failed to fetch data for ticker {tickers}: {e}")


all_stocks = pd.read_excel("stocks.xlsx")
first_100_stocks = all_stocks['ticker'].tolist()
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

# Convert the annual risk-free rate to a daily rate
rf_annual = 0.01  # 1% annual rate
rf_daily = (1 + rf_annual) ** (1 / 365) - 1
rf_daily

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
