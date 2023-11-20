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
    login_form = LoginForm(prefix='login')  # Ajoutez un préfixe pour différencier les formulaires
    register_form = RegisterForm(prefix='register')  # Ajoutez un préfixe pour différencier les formulaires
    print("try")
    # Logique de connexion
    if login_form.validate_on_submit() and 'login' in request.form:
        print("login")
        attempted_user = users.query.filter_by(email=login_form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=login_form.password.data):
            print("if")
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.name}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password do not match! Please try again', category='danger')

    # Logique d'inscription
    if register_form.validate_on_submit() and 'register' in request.form:
        print("here")
        user_to_create = users(
            name=register_form.name.data,
            email=register_form.email_address.data,
            password=register_form.password1.data,  # This will call the setter
            birthdate=register_form.birthdate.data
        )
        print(user_to_create)
        db.session.add(user_to_create)
        db.session.commit()
        print("sucess")
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.name}", category='success')
        return redirect(url_for('home_page'))

    if register_form.errors != {}:  # If there are errors from the validations
        for err_msg in register_form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('login.html', login_form=login_form, register_form=register_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = users(name=form.name.data,
                              email=form.email_address.data,
                              password=form.password1.data,
                               birthdate=form.birthdate.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    register_form = RegisterForm()  # Si vous avez également besoin d'afficher le formulaire d'inscription sur la même page
    if login_form.validate_on_submit():
        attempted_user = users.query.filter_by(email=login_form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=login_form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.name}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', login_form=login_form, register_form=register_form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))










