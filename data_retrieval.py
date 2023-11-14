from config import *
from portfolio_analysis import calculate_returns

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

