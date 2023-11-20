from main import *
from neoma import app
from flask import render_template, redirect, url_for, flash, request, session
from neoma.models import *
from neoma.forms import *
from neoma import db
from flask_login import *

from portfolio_analysis import best_weigth


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')


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
    if 'portfolio_bool' not in session:
        crypto_weight_limit, stocks_data, crypto_data, capital, Top_5_Selection = recommend_and_display_portfolio(
            session['portfolio_type'], session['capital'], session['investment_horizon'], session['nb_stocks'])
        top_5_transformed = transform_top_5_selection(Top_5_Selection)

        plot_data = generate_plotly_data(top_5_transformed)

    if PortfolioSelection.validate_on_submit():
        session['portfolio_bool'] = True
        selected_portfolio_number = int(PortfolioSelection.portfolio_choice.data)
        selected_portfolio = top_5_transformed[selected_portfolio_number]

        # Extract stocks and cryptos from the selected portfolio
        selected_stocks = selected_portfolio.get('stocks', [])
        selected_cryptos = selected_portfolio.get('cryptos', [])

        (combined_selected_assets, monetary_allocation, best_weights, ret_arr_allocation, vol_arr_allocation
         , sharpe_arr_allocation) = best_weigth(crypto_weight_limit, stocks_data, crypto_data, capital, selected_stocks,
                                                selected_cryptos)

        plot_data = generate_optimal_weight_plot_data(vol_arr_allocation, ret_arr_allocation, sharpe_arr_allocation)
        max_sharpe_idx = sharpe_arr_allocation.argmax()
        data_portfolio = [ret_arr_allocation[max_sharpe_idx], vol_arr_allocation[max_sharpe_idx]
            , sharpe_arr_allocation[max_sharpe_idx]]

        list_weight_selected_assets_json = json.dumps(best_weights.tolist())
        data_portfolio_json = json.dumps([arr.tolist() for arr in data_portfolio])


        new_portfolio = Portfolio(
            user_id=current_user.id,
            name='User Portfolio',
            list_selected_assets=json.dumps(selected_stocks + selected_cryptos),
            list_weight_selected_assets=list_weight_selected_assets_json,
            data_portfolio=data_portfolio_json,
            is_invested=False,
            capital=capital,
            horizon=session['investment_horizon'],
        )
        db.session.add(new_portfolio)
        db.session.commit()
        session.pop('portfolio_bool', None)
        return render_template('plot_choosen_portfolio.html', plot_data=plot_data,data=data_portfolio)

    return render_template('plot_portfolios.html', plot_data=plot_data, form=PortfolioSelection)
romain