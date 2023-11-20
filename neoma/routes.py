from neoma import app
from flask import render_template, redirect, url_for, flash, request
from neoma.models import users
from neoma.forms import RegisterForm, LoginForm
from neoma import db
from flask_login import login_user, logout_user, login_required, current_user

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










