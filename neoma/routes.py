from main import *
from neoma import app
from flask import render_template, redirect, url_for, flash, request
from neoma.models import users
from neoma.forms import *
from neoma import db
from flask_login import *


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
            flash('Investment details submitted successfully!', 'success')
            # Use recommend_and_display_portfolio function
            combined_selected_assets,monetary_allocation,best_weights = recommend_and_display_portfolio(
                portfolio_type, capital, investment_horizon, nb_stocks)
            print(combined_selected_assets,monetary_allocation,best_weights)
            # Redirect or perform other actions after processing both forms
            return redirect(url_for('home_page'))
        else:
            # Handle the situation if one or both forms are invalid
            flash('Please correct the errors in the form.', 'danger')

    return render_template('build_portfolio.html', risk_form=risk_form, investment_form=investment_form)









