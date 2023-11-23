from io import BytesIO
import json

from neoma import app, cache
from flask import render_template, redirect, send_file, url_for, flash, request, session
from neoma.models import *
from neoma.forms import *
from neoma import db
from flask_login import *

from plotting import generate_plotly_data, generate_optimal_weight_plot_data
from portfolio_analysis import best_weigth, recommend_portfolio
from flask import jsonify


@app.route('/loading_status')
def loading_status():
    progress = cache.get("data_fetch_progress") or 0
    return jsonify({"progress": progress})



@app.route('/')
@app.route('/home')
def home_page():
    plotting_data = cache.get("plotting_data")
    if plotting_data:
        print("Plotting data available.")
        # Use plotting_data for response
    else:
        print("Plotting data not yet available.")

    return render_template('index.html',data=plotting_data)


@app.route('/login_register', methods=['GET', 'POST'])
def login_register_page():
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
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))


@app.route('/combined_survey_investment', methods=['GET', 'POST'])
@login_required
def combined_survey_investment():
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


@app.route('/select_portfolio', methods=['GET', 'POST'])
@login_required
def portfolio_options():
    PortfolioSelection = PortfolioSelectionForm()

    if 'top_5_portfolios' in session:
        plot_data = generate_plotly_data(session['top_5_portfolios'])
        session.pop('top_5_portfolios', None)

    else:
        plotting_data = cache.get("plotting_data")
        crypto_weight_limit, stocks_data, crypto_data, capital, Top_5_Selection = recommend_portfolio(
            session['nb_stocks'],plotting_data["Stocks"]["data_stocks"],plotting_data["Cryptos"]["data_crypto"],session['capital'],session['portfolio_type'], session['investment_horizon'])
        top_5_transformed = transform_top_5_selection(Top_5_Selection)
        plot_data = generate_plotly_data(top_5_transformed)

        if PortfolioSelection.validate_on_submit():
            session['top_5_portfolios'] = top_5_transformed
            session['portfolio_bool'] = True
            selected_portfolio_number = int(PortfolioSelection.portfolio_choice.data)-1
            selected_portfolio = top_5_transformed[selected_portfolio_number]
            # Extract stocks and cryptos from the selected portfolio
            selected_stocks = selected_portfolio.get('stocks', [])
            selected_cryptos = selected_portfolio.get('cryptos', [])

            isin_mapping = plotting_data["Stocks"]["list_isin"]
            ticker_mapping = plotting_data["Stocks"]["symbols"]
            if len(ticker_mapping) != len(isin_mapping):
                raise ValueError("Ticker and ISIN lists must be of the same length")
            ticker_to_isin = dict(zip(ticker_mapping, isin_mapping))
            # Retrieve ISINs for the selected stocks
            selected_stock_isins = [ticker_to_isin.get(ticker) for ticker in selected_stocks if
                                    ticker in ticker_to_isin]
            # Retrieve ISINs for the selected stocks
            (combined_selected_assets, monetary_allocation, best_weights, ret_arr_allocation, vol_arr_allocation
             , sharpe_arr_allocation,all_alphas, all_betas, best_portfolio_beta, best_portfolio_alpha) = best_weigth(crypto_weight_limit, stocks_data, crypto_data, capital,
                                                    selected_stocks,
                                                    selected_cryptos,ticker_to_isin,plotting_data)
            plot_data = generate_optimal_weight_plot_data(vol_arr_allocation, ret_arr_allocation, sharpe_arr_allocation)
            max_sharpe_idx = sharpe_arr_allocation.argmax()
            data_portfolio = [ret_arr_allocation[max_sharpe_idx], vol_arr_allocation[max_sharpe_idx]
                , sharpe_arr_allocation[max_sharpe_idx]]
            list_weight_selected_assets_json = json.dumps(best_weights.tolist())

            capital_allocation = [weight * capital for weight in best_weights]
            # Combine the assets, weights, and capital into a single list for the template
            assets_info = [
                f"{asset} ({weight * 100:.1f}% - {cap:.2f}€)"
                for asset, weight, cap in zip(combined_selected_assets, best_weights, capital_allocation)
            ]
            future_value = capital * ((1 + ret_arr_allocation[max_sharpe_idx]) ** session['investment_horizon'])
            new_portfolio = Portfolio(
                user_id=current_user.id,
                name='User Portfolio',
                list_selected_assets=json.dumps(selected_stocks + selected_cryptos),
                list_weight_selected_assets=list_weight_selected_assets_json,
                data_portfolio=json.dumps(data_portfolio),
                is_invested=False,
                capital=capital,
                horizon=session['investment_horizon'],
                future_value = json.dumps(future_value),
                list_plotdata =json.dumps( plot_data),
                assets_info = json.dumps(assets_info)
            )
            db.session.add(new_portfolio)
            db.session.commit()
            session.pop('portfolio_bool', None)

            return render_template('plot_choosen_portfolio.html', plot_data=plot_data, data=data_portfolio,
                                   fv=round(future_value, 3),portfolio_details=assets_info)
    return render_template('plot_portfolios.html', plot_data=plot_data, form=PortfolioSelection)


@app.route('/my_portfolio', methods=['GET', 'POST'])
@login_required
def my_portfolio():

    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()

    for portfolio in portfolios:
        # Ensure that list_selected_assets is a proper JSON string
        # You might need to adjust this part if list_selected_assets is already a list or formatted differently
        assets_list = json.loads(portfolio.list_selected_assets)
        weights_list = json.loads(portfolio.list_weight_selected_assets)
        # Separate stocks and cryptocurrencies
        stocks = [asset for asset in assets_list if not asset.endswith('-USD')]
        cryptos = [asset for asset in assets_list if asset.endswith('-USD')]

        crypto_weights = sum(weights_list[i] for i, asset in enumerate(assets_list) if asset.endswith('-USD'))*100
        stock_weights = sum(weights_list[i] for i, asset in enumerate(assets_list) if not asset.endswith('-USD'))*100

        # Store the weights as percentages
        portfolio.crypto_weight_percentage = round(crypto_weights,2)
        portfolio.stock_weight_percentage = round(stock_weights,2)

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
        # Handle the error if plotting_data is not found in the cache
        return "Error: Plotting data not found", 500

    # Récupérez les données de votre modèle de base de données
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio_name = portfolio.name  # Supposition que 'name' est un champ dans votre modèle

    # Convertissez la liste des actifs sélectionnés en DataFrame
    selected_assets = pd.DataFrame(json.loads(portfolio.list_selected_assets))
    print(selected_assets.head())
    # Initialisez un DataFrame vide pour les prix
    prices = pd.DataFrame()

    # Parcourez chaque actif et récupérez ses données de prix
    for asset in selected_assets.iloc[:, 0]:
    # Vérifiez si l'actif est une crypto-monnaie, une action ou un indice
        if asset in plotting_data["Cryptos"]["symbols"]:
            asset_prices = plotting_data["Cryptos"]["data_crypto"].get(asset)
        elif asset in plotting_data["Stocks"]["symbols"]:
            asset_prices = plotting_data["Stocks"]["data_stocks"].get(asset)
        else:
            return f"Error: Asset type for {asset} not found", 500

    # Vérifiez si les prix de l'actif ont été trouvés
    if asset_prices is not None:
        prices[asset] = pd.Series(asset_prices)
    else:
        return f"Error: Prices for asset {asset} not found", 500

    # Calculez les rendements quotidiens
    daily_returns = prices.pct_change()

    # Créez le fichier Excel et ajoutez une nouvelle feuille avec les rendements quotidiens
    with pd.ExcelWriter('rendements_et_risques.xlsx', engine='openpyxl', mode='a') as writer:
        sheet_name = f'Rendement_{portfolio_name}'
        daily_returns.to_excel(writer, sheet_name=sheet_name)

    # Lisez le fichier mis à jour pour l'envoyer
    output = BytesIO()
    with open('rendements_et_risques.xlsx', 'rb') as f:
        output.write(f.read())

    # Retournez le fichier Excel en tant que réponse téléchargeable
    output.seek(0)
    
    return send_file(output, as_attachment=True, attachment_filename='rendements_et_risques.xlsx')