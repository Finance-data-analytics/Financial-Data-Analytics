import io
from io import BytesIO
import json
from scipy.stats import norm
from project import app, cache
from flask import render_template, redirect, send_file, url_for, flash, request, session
from project.models import *
from project.forms import *
from project import db
from flask_login import *
from plotting import generate_plotly_data, generate_optimal_weight_plot_data
from portfolio_analysis import best_weigth, recommend_portfolio
from flask import jsonify
import numpy as np


def clear_portfolio_data_from_session():
    # List of keys to keep (related to authentication)
    keys_to_keep = {'_fresh', 'csrf_token', '_user_id', '_id'}

    # Create a list of keys to delete
    keys_to_delete = [key for key in session.keys() if key not in keys_to_keep]

    # Delete the keys related to portfolio data
    for key in keys_to_delete:
        session.pop(key, None)


@app.route('/loading_status')
def loading_status():
    progress = cache.get("data_fetch_progress") or cache.get("finale_progress")
    print(progress)
    return jsonify({"progress": progress})


@app.route('/check_plotting_data')
def check_plotting_data():
    plotting_data = cache.get("plotting_data")
    if plotting_data:
        print("Plotting data available.")
        # Use plotting_data for response
    else:
        print("Plotting data not yet available.")
    return jsonify({'isLoaded': plotting_data is not None})


@app.route('/')
@app.route('/home')
def home_page():
    clear_portfolio_data_from_session()
    plotting_data = cache.get("plotting_data")
    if plotting_data:
        print("Plotting data available.")
        # Use plotting_data for response
    else:
        print("Plotting data not yet available.")

    return render_template('index.html')


@app.route('/login_register', methods=['GET', 'POST'])
def login_register_page():
    clear_portfolio_data_from_session()
    login_form = LoginForm(prefix='login')
    register_form = RegisterForm(prefix='register')
    # Logique de connexion
    if 'login-submit' in request.form and login_form.validate_on_submit():
        attempted_user = users.query.filter_by(email=login_form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=login_form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.name}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password do not match! Please try again', category='danger')
    # Logique d'inscription
    if 'register-submit' in request.form and register_form.validate_on_submit():
        user_to_create = users(
            name=register_form.name.data,
            email=register_form.email_address.data,
            password=register_form.password1.data,  # This will call the setter
            birthdate=register_form.birthdate.data
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.name}", category='success')
        return redirect(url_for('home_page'))
    if register_form.errors != {}:  # If there are errors from the validations
        for err_msg in register_form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('login.html', login_form=login_form, register_form=register_form)


@app.route('/logout')
def logout_page():
    logout_user()
    session.clear()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))


@app.route('/combined_survey_investment', methods=['GET', 'POST'])
@login_required
def combined_survey_investment():
    clear_portfolio_data_from_session()
    risk_form = RiskAversionSurveyForm(prefix='risk')
    investment_form = InvestmentForm(prefix='investment')
    if request.method == 'POST':
        # Extract values from slider inputs and convert them to the correct type
        # before validation since they come as strings from the request
        investment_form.capital.data = float(request.form.get('capital', 0))
        investment_form.investment_horizon.data = int(request.form.get('investment_horizon', 1))
        investment_form.nb_assets.data = int(request.form.get('nb_assets', 1))
        # Validate both forms
        risk_form_valid = risk_form.validate()
        investment_form_valid = investment_form.validate()
        if risk_form_valid and investment_form_valid:
            # Process risk form data
            total_score = evaluate_risk_aversion_from_form(risk_form)
            portfolio_type = suggest_portfolio(total_score)
            flash(f'Your recommended portfolio type is: {portfolio_type}', 'success')
            # Process investment form data
            capital = investment_form.capital.data
            investment_horizon = investment_form.investment_horizon.data
            nb_stocks = investment_form.nb_assets.data
            # Store the data in the session
            session['portfolio_type'] = portfolio_type
            session['capital'] = capital
            session['nb_stocks'] = nb_stocks
            session['investment_horizon'] = investment_horizon
            flash('Investment details submitted successfully!', 'success')
            # Rediriger vers la route 'portfolio_options'
            return redirect(url_for('portfolio_options'))
            # Redirect or perform other actions after processing both forms
        else:
            # Handle the situation if one or both forms are invalid
            flash('Please correct the errors in the form.', 'danger')
    return render_template('build_portfolio.html', risk_form=risk_form, investment_form=investment_form)


def get_plot_data():
    plotting_data = cache.get("plotting_data")
    stocks_data_original = plotting_data["Stocks"]["data_stocks"]

    # Create a new DataFrame from the original to avoid modifying it directly
    stocks_data_filtered = plotting_data["Stocks"]["data_stocks"].copy()

    # Iterate over the columns of the DataFrame
    for column in stocks_data_filtered.columns:
        # Check the last value of the column
        print("Last value in column:", stocks_data_filtered[column].iloc[-1])
        print("Type of last value:", type(stocks_data_filtered[column].iloc[-1]))
        print("Capital:", session['capital'])
        print("Type of capital:", type(session['capital']))

        if stocks_data_filtered[column].iloc[-1] > session['capital']:
            # Drop the column if the last value is greater than capital
            stocks_data_filtered.drop(column, axis=1, inplace=True)

    crypto_weight_limit, stocks_data, crypto_data, capital, Top_5_Selection = recommend_portfolio(
        session['nb_stocks'], stocks_data_filtered, plotting_data["Cryptos"]["data_crypto"],
        session['capital'], session['portfolio_type'], session['investment_horizon'])

    top_5_transformed = transform_top_5_selection(Top_5_Selection)

    plot_data = generate_plotly_data(top_5_transformed)
    return plot_data, top_5_transformed, crypto_weight_limit, stocks_data, crypto_data, capital


def extract_selected_data(PortfolioSelection):
    selected_portfolio_number = int(PortfolioSelection.portfolio_choice.data) - 1
    selected_portfolio = session['top_5_portfolios'][selected_portfolio_number]
    # Extract stocks and cryptos from the selected portfolio
    selected_stocks = selected_portfolio.get('stocks', [])
    selected_cryptos = selected_portfolio.get('cryptos', [])

    session['selected_stocks'] = selected_stocks
    session['selected_cryptos'] = selected_cryptos


def create_portfolio_session_data(crypto_weight_limit, capital, stocks_data, crypto_data, ticker_to_isin,
                                  plotting_data):
    (combined_selected_assets, monetary_allocation, best_weights, ret_arr_allocation, vol_arr_allocation,
     sharpe_arr_allocation, all_alphas, all_betas, best_portfolio_beta, best_portfolio_alpha) = best_weigth(
        crypto_weight_limit, stocks_data, crypto_data, capital,
        session['selected_stocks'], session['selected_cryptos'], ticker_to_isin, plotting_data)

    session['list_weight_selected_assets_json'] = json.dumps(best_weights.tolist())
    capital_allocation = [weight * capital for weight in best_weights]
    max_sharpe_idx = sharpe_arr_allocation.argmax()
    future_value = capital * ((1 + ret_arr_allocation[max_sharpe_idx]) ** session['investment_horizon'])

    flattened_alphas = all_alphas
    flattened_betas = all_betas

    # Store the calculated data in session
    session.update({
        'plot_data': generate_optimal_weight_plot_data(vol_arr_allocation, ret_arr_allocation, sharpe_arr_allocation),
        'data_portfolio': [ret_arr_allocation[max_sharpe_idx], vol_arr_allocation[max_sharpe_idx],
                           sharpe_arr_allocation[max_sharpe_idx], all_alphas, all_betas, best_portfolio_beta,
                           best_portfolio_alpha],
        'assets_info': [f"{asset} ({weight * 100:.1f}% - {cap:.2f}€ - β {beta:.2f} - α {alpha:.2f})"
                        for asset, weight, cap,alpha,beta in zip(combined_selected_assets, best_weights, capital_allocation,flattened_alphas,flattened_betas)],
        'future_value': future_value
    })

    return future_value


@app.route('/select_portfolio', methods=['GET', 'POST'])
@login_required
def portfolio_options():
    PortfolioSelection = PortfolioSelectionForm()

    if 'top_5_portfolios' in session:
        plot_data = generate_plotly_data(session['top_5_portfolios'])
        session.pop('top_5_portfolios', None)
    else:
        plot_data, top_5_transformed, crypto_weight_limit, stocks_data, crypto_data, capital = get_plot_data()

        if PortfolioSelection.validate_on_submit():
            session['top_5_portfolios'] = top_5_transformed
            extract_selected_data(PortfolioSelection)

            # Validate ticker and ISIN mapping
            plotting_data = cache.get("plotting_data")
            isin_mapping = plotting_data["Stocks"]["list_isin"]
            ticker_mapping = plotting_data["Stocks"]["symbols"]
            if len(ticker_mapping) != len(isin_mapping):
                raise ValueError("Ticker and ISIN lists must be of the same length")
            ticker_to_isin = dict(zip(ticker_mapping, isin_mapping))

            future_value = create_portfolio_session_data(crypto_weight_limit, capital, stocks_data, crypto_data,
                                                         ticker_to_isin, plotting_data)
            return render_template('plot_choosen_portfolio.html', plot_data=session['plot_data'],
                                   data=session['data_portfolio'], fv=round(future_value, 3),
                                   portfolio_details=session['assets_info'])

    return render_template('plot_portfolios.html', plot_data=plot_data, form=PortfolioSelection)


@app.route('/my_portfolio', methods=['GET', 'POST'])
@login_required
def my_portfolio():
    clear_portfolio_data_from_session()
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    for portfolio in portfolios:
        # Ensure that list_selected_assets is a proper JSON string
        # You might need to adjust this part if list_selected_assets is already a list or formatted differently
        assets_list = json.loads(portfolio.list_selected_assets)
        weights_list = json.loads(portfolio.list_weight_selected_assets)
        # Separate stocks and cryptocurrencies
        stocks = [asset for asset in assets_list if not asset.endswith('-USD')]
        cryptos = [asset for asset in assets_list if asset.endswith('-USD')]

        crypto_weights = sum(weights_list[i] for i, asset in enumerate(assets_list) if asset.endswith('-USD')) * 100
        stock_weights = sum(weights_list[i] for i, asset in enumerate(assets_list) if not asset.endswith('-USD')) * 100

        # Store the weights as percentages
        portfolio.crypto_weight_percentage = round(crypto_weights, 2)
        portfolio.stock_weight_percentage = round(stock_weights, 2)

        # Store them back in the portfolio object, possibly in new attributes
        portfolio.stocks = stocks
        portfolio.cryptos = cryptos

    app.jinja_env.filters['format_currency'] = format_currency
    # Ajoutez la fonction au contexte Jinja pour l'utiliser dans le template
    app.jinja_env.filters['format_assets'] = format_assets
    if not portfolios:
        print("No portfolios found for user.")

    return render_template('myPortfolio.html', portfolios=portfolios)


@login_required
@app.route('/rename_portfolio', methods=['POST'])
def rename_portfolio():
    portfolio_id = request.form.get('portfolio_id')
    new_name = request.form.get('new_name')
    portfolio = Portfolio.query.get(portfolio_id)
    if portfolio and portfolio.user_id == current_user.id:
        portfolio.name = new_name
        db.session.commit()
        flash('Portfolio renamed successfully!', 'success')
    else:
        flash('Portfolio not found or access denied', 'error')
    return redirect(url_for('my_portfolio'))


@login_required
@app.route('/delete_portfolio/<int:portfolio_id>', methods=['GET'])
def delete_portfolio(portfolio_id):
    # Logique pour trouver le portfolio par ID et le supprimer de la base de données
    portfolio_to_delete = Portfolio.query.get(portfolio_id)
    if portfolio_to_delete:
        db.session.delete(portfolio_to_delete)
        db.session.commit()
        flash('Portfolio deleted successfully', 'success')
    else:
        flash('Portfolio not found', 'error')

    return redirect(url_for('my_portfolio'))


@app.route('/see_details/<int:portfolio_id>', methods=['GET'])
@login_required
def see_details(portfolio_id):
    # Fetch the portfolio from the database
    portfolio = Portfolio.query.get_or_404(portfolio_id)

    # Assuming you have stored JSON data in your Portfolio model
    # and you have a method to transform this data into a plotly readable format
    list_plotdata = json.loads(portfolio.list_plotdata)
    data_portfolio = json.loads(portfolio.data_portfolio)
    # The future value and portfolio details can be directly accessed if they're columns in your model
    future_value = portfolio.future_value
    assets_info = json.loads(portfolio.assets_info)  # This should be a serializable field, such as a JSON string

    # Now you can render your template with the gathered data
    return render_template('seeDetails.html',
                           portfolio=portfolio,
                           plot_data=list_plotdata,
                           data=data_portfolio,
                           fv=future_value,
                           portfolio_details=assets_info)


@app.route('/download_portfolio_returns/<int:portfolio_id>')
@login_required
def download_portfolio_returns(portfolio_id):
    plotting_data = cache.get("plotting_data")

    if not plotting_data:
        return "Error: Plotting data not found", 500

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio_name = portfolio.name

    # Ici, nous récupérons la valeur future comme étant la valeur totale du portefeuille
    portfolio_value = portfolio.future_value

    selected_assets = pd.DataFrame(json.loads(portfolio.list_selected_assets))
    weights = pd.DataFrame(json.loads(portfolio.list_weight_selected_assets))  # Assurez-vous que ceci est correct
    prices = pd.DataFrame()

    for asset in selected_assets.iloc[:, 0]:
        if asset in plotting_data["Cryptos"]["symbols"]:
            asset_prices = plotting_data["Cryptos"]["data_crypto"].get(asset)
        elif asset in plotting_data["Stocks"]["symbols"]:
            asset_prices = plotting_data["Stocks"]["data_stocks"].get(asset)
        else:
            return f"Error: Asset type for {asset} not found", 500

        if asset_prices is not None:
            prices[asset] = pd.Series(asset_prices)
        else:
            return f"Error: Prices for asset {asset} not found", 500

    daily_returns = prices.pct_change().dropna()
    cov_matrix = daily_returns.cov()

    # Ici, nous supposons que les poids sont stockés dans un DataFrame avec la même ordre que `selected_assets`
    asset_weights = weights.values.flatten()  # Vous devez vous assurer que les poids sont correctement alignés avec `selected_assets`
    portfolio_volatility = np.sqrt(np.dot(asset_weights.T, np.dot(cov_matrix, asset_weights)))

    # Calculs de la VaR
    var_95 = norm.ppf(1 - 0.95) * portfolio_volatility * portfolio_value
    var_99 = norm.ppf(1 - 0.99) * portfolio_volatility * portfolio_value

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        daily_returns.to_excel(writer, sheet_name='Rendements Quotidiens')
        var_df = pd.DataFrame({'VaR 95%': [var_95], 'VaR 99%': [var_99]})
        var_df.to_excel(writer, sheet_name='VaR')

    output.seek(0)
    filename = f"{portfolio_name}_rendements_et_risques.xlsx"

    return send_file(output, as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@login_required
@app.route('/add_portfolio', methods=['GET'])
def add_portfolio():
    plotting_data = cache.get("plotting_data")
    new_portfolio = Portfolio(
        user_id=current_user.id,
        name='User Portfolio',
        list_selected_assets=json.dumps(session['selected_stocks'] + session['selected_cryptos']),
        list_weight_selected_assets=session['list_weight_selected_assets_json'],
        data_portfolio=json.dumps(session['data_portfolio']),
        is_invested=False,
        capital=session['capital'],
        horizon=session['investment_horizon'],
        future_value=json.dumps(session['future_value']),
        list_plotdata=json.dumps(session['plot_data']),
        assets_info=json.dumps(session['assets_info'])
    )
    db.session.add(new_portfolio)
    db.session.commit()
    clear_portfolio_data_from_session()
    return render_template('index.html', data=plotting_data)