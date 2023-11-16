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
    stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'PAX', 'USDP','UNI']

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


def get_data_crypto(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data


def get_data_stocks(tickers, isins, start_date, end_date):
    successful_retrievals = []
    data_list = []
    for index, (ticker, isin) in enumerate(zip(tickers, isins)):
        try:
            print(f"Processing {index + 1}/{len(tickers)}: {ticker}/{isin}")
            data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']

            if data.empty or data.isna().any():
                data = yf.download(isin, start=start_date, end=end_date)['Adj Close']
            if not data.empty and not data.isna().any():
                successful_retrievals.append(ticker)  # Use isin if ISIN was successful
                data.name = ticker  # Use isin as the name if ISIN was successful
                data_list.append(data)
            else:
                print(f"Data for {ticker}/{isin} was still empty or contained NaNs after retrieval.")

        except Exception as e:
            print(f"Failed to retrieve data for {ticker}/{isin}: {e}")

    if data_list:
        all_data = pd.concat(data_list, axis=1)
    else:
        all_data = pd.DataFrame()

    return all_data, successful_retrievals


all_stocks = pd.read_excel("stocks.xlsx")
ticker = all_stocks['ticker'][:10].tolist()
isin = all_stocks['isin'][:10].tolist()
list_ticker = [str(ticker) for ticker in ticker]

crypto_data = get_data_crypto(crypto_symbols, '2019-01-01', '2023-10-01')
stocks_data, successful_symbols = get_data_stocks(list_ticker, isin, '2019-01-01', '2023-10-01')

crypto_daily_returns = calculate_returns(crypto_data)
stocks_daily_returns = calculate_returns(stocks_data)

# Calculate average daily returns and risks for crypto and stocks
crypto_avg_daily_returns = crypto_daily_returns.mean()
stocks_avg_daily_returns = stocks_daily_returns.mean()

crypto_risks = crypto_daily_returns.std()
stocks_risks = stocks_daily_returns.std()

# Filter out assets with zero avg return and risk in crypto data
crypto_to_keep = ~(crypto_avg_daily_returns == 0) | ~(crypto_risks == 0)
crypto_daily_returns_filtered = crypto_daily_returns.loc[:, crypto_to_keep]
crypto_avg_daily_returns_filtered = crypto_avg_daily_returns[crypto_to_keep]
crypto_risks_filtered = crypto_risks[crypto_to_keep]

# Filter out assets with zero avg return and risk in stocks data
stocks_to_keep = ~(stocks_avg_daily_returns == 0) | ~(stocks_risks == 0)
stocks_daily_returns_filtered = stocks_daily_returns.loc[:, stocks_to_keep]
stocks_avg_daily_returns_filtered = stocks_avg_daily_returns[stocks_to_keep]
stocks_risks_filtered = stocks_risks[stocks_to_keep]


# Create dictionary of results with filtered data
results_dict = {
    "Stocks": pd.DataFrame({
        "Rendement moyen": stocks_avg_daily_returns_filtered,
        "Risque": stocks_risks_filtered
    }),
    "Crypto": pd.DataFrame({
        "Rendement moyen": crypto_avg_daily_returns_filtered,
        "Risque": crypto_risks_filtered
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
    "Stocks": (stocks_avg_daily_returns_filtered, stocks_daily_returns_filtered),
    "Crypto": (crypto_avg_daily_returns_filtered, crypto_daily_returns_filtered)
}

# Empty dictionary to store efficient portfolios for each asset type
efficient_portfolios_dict = {}

# Loop over the dictionary
for asset_type, (avg_daily_returns, daily_returns) in data_dict.items():
    target_returns = np.linspace(avg_daily_returns.min(), avg_daily_returns.max(), 100)
    efficient_portfolios = [efficient_frontier(daily_returns, target_return) for target_return in target_returns]
    efficient_portfolios_dict[asset_type] = efficient_portfolios


# Convert the annual risk-free rate to a daily rate
rf_annual = 0.0455  # 1% annual rate
rf_daily = (1 + rf_annual)**(1/365) - 1
rf_daily

file_path = "rendements_et_risques.xlsx"

# Read the first column from the 'Stocks' sheet, skipping the first row
stocks_actualised = pd.read_excel(file_path, sheet_name='Stocks', usecols=[0], skiprows=0)
stocks_actualised = stocks_actualised.iloc[:, 0].tolist()

# Read the first column from the 'Crypto' sheet, skipping the first row
crypto_actualised = pd.read_excel(file_path, sheet_name='Crypto', usecols=[0], skiprows=0)
crypto_actualised = crypto_actualised.iloc[:, 0].tolist()


# Dictionary containing data for plotting
plotting_data = {
    "Cryptos": {
        "risks": crypto_risks_filtered,
        "avg_daily_returns": crypto_avg_daily_returns_filtered,
        "symbols": crypto_actualised,
        "efficient_portfolios": efficient_portfolios_dict["Crypto"],
        "color": 'b',
        "title": 'Cryptos: Rendement vs Risque'
    },
    "Stocks": {
        "risks": stocks_risks_filtered,
        "avg_daily_returns": stocks_avg_daily_returns_filtered,
        "symbols": stocks_actualised,
        "efficient_portfolios": efficient_portfolios_dict["Stocks"],
        "color": 'r',
        "title": 'Stocks: Rendement vs Risque',
        "list_ticker_isin":successful_symbols
    }
}