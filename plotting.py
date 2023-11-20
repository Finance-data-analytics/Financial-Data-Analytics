import json

import plotly

from config import *

def plot_assets_and_cal(data_dict, rf_daily):
    # Loop over the dictionary to plot for each asset type
    for key, data in data_dict.items():
        plt.figure(figsize=(12, 6))
        # Plotting the efficient frontier


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


def generate_plotly_data(top_selections):
    plot_data = []

    colors = ['red', 'green', 'blue', 'orange', 'purple']  # Définir une liste de couleurs

    for i, selection in enumerate(top_selections, start=1):
        plot = {
            'x': [selection['volatility']],
            'y': [selection['return']],
            'type': 'scatter',
            'mode': 'markers+text',
            'name': f'Top {i}',
            'text': [f'Choice {i}: Score {selection["score"]:.2f}'],  # Ajouter le numéro de choix ici
            'textposition': 'top center',
            'marker': {
                'color': colors[i-1],  # Utiliser une couleur de la liste définie ci-dessus
                'size': 10  # Vous pouvez ajuster la taille si nécessaire
            }
        }
        plot_data.append(plot)

    return json.dumps(plot_data)  # Convertir en JSON pour passer au template


def generate_optimal_weight_plot_data(vol_arr_allocation, ret_arr_allocation, sharpe_arr_allocation):
    plot_data = []

    # Convert NumPy arrays to Python lists
    vol_arr_list = vol_arr_allocation.tolist()
    ret_arr_list = ret_arr_allocation.tolist()
    sharpe_arr_list = sharpe_arr_allocation.tolist()

    # Create the main scatter plot for all portfolios
    main_trace = {
        'x': vol_arr_list,
        'y': ret_arr_list,
        'mode': 'markers',
        'type': 'scatter',
        'marker': {
            'size': 8,
            'color': sharpe_arr_list,  # Color according to Sharpe Ratio
            'colorscale': 'Viridis',
            'showscale': True,
            'colorbar': {
                'title': 'Sharpe Ratio'
            }
        },
        'name': 'Portfolios'
    }
    plot_data.append(main_trace)

    # Highlight the best portfolio
    max_sharpe_idx = np.argmax(sharpe_arr_allocation)
    best_portfolio_trace = {
        'x': [vol_arr_list[max_sharpe_idx]],
        'y': [ret_arr_list[max_sharpe_idx]],
        'mode': 'markers',
        'type': 'scatter',
        'marker': {
            'size': 14,
            'color': 'red',
            'line': {
                'width': 2,
                'color': 'Black'
            }
        },
        'name': 'Best Portfolio'
    }
    plot_data.append(best_portfolio_trace)

    # Convert the plot data to JSON for rendering with Plotly in the template
    return json.dumps(plot_data)