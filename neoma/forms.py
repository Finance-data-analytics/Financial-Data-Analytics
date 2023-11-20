from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from neoma.models import users


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = users.query.filter_by(name=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = users.query.filter_by(email=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    name = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    birthdate = DateField(label = 'BirthDate',validators=[DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    email = StringField(label='email:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class RiskAversionSurveyForm(FlaskForm):
    question1 = RadioField('1. What is your age?', choices=[('a', 'Under 30'), ('b', '30-50 years'), ('c', 'Over 50 years')], validators=[DataRequired()])
    question2 = RadioField('2. What is your investment experience?', choices=[('a', 'Beginner'), ('b', 'Intermediate'), ('c', 'Experienced')], validators=[DataRequired()])
    question3 = RadioField('3. What is your investment horizon?', choices=[('a', 'Short term (less than 5 years)'), ('b', 'Medium term (5-10 years)'), ('c', 'Long term (more than 10 years)')], validators=[DataRequired()])
    question4 = RadioField('4. What percentage of your investment are you willing to lose to obtain better returns?', choices=[('a', 'Less than 10%'), ('b', '10-30%'), ('c', 'More than 30%')], validators=[DataRequired()])
    question5 = RadioField('5. How would you react if your investments lost 10% of their value in a short period of time?', choices=[('a', 'Buy more'), ('b', 'Make no changes'), ('c', 'Sell all investments')], validators=[DataRequired()])
    question6 = RadioField('6. Are you considering alternative investments (like cryptocurrencies, real estate, commodities, etc.)?', choices=[('a', 'No, I prefer traditional investments'), ('b', 'Yes, but only a small portion of my portfolio'), ('c', 'Yes, I am open to a significant proportion in alternative investments')], validators=[DataRequired()])
    question7 = RadioField('7. If an investment does not perform as expected after one year, what would be your action?', choices=[('a', 'Sell immediately to limit losses'), ('b', 'Reevaluate the situation, but probably maintain the investment'), ('c', 'Keep the investment because I believe in long-term benefits')], validators=[DataRequired()])
    question8 = RadioField('8. Which of the following statements best describes your knowledge of investing?', choices=[('a', 'My knowledge of investments and financial markets is limited.'), ('b', 'I have some knowledge of investments and financial markets.'), ('c', 'I have solid knowledge of investments.')], validators=[DataRequired()])
    question9 = RadioField('9. What is your main objective in investing?', choices=[('a', 'Preserve capital and maintain stable growth'), ('b', 'Balance growth and security, with a moderate approach'), ('c', 'Seek high growth, even if it means greater risk.')], validators=[DataRequired()])
    question10 = RadioField('10. Faced with a very popular new investment trend, like a speculative bubble, what would be your approach?', choices=[('a', 'Avoid completely, too risky for my taste'), ('b', 'Invest a small amount not to miss a potential opportunity'), ('c', 'Invest significantly, hoping to make a big profit.')], validators=[DataRequired()])
    question11 = RadioField('11. Do you wish to include cryptocurrencies in your portfolio?', choices=[('a', 'Yes'), ('b', 'No')], validators=[DataRequired()])
    submit = SubmitField('Submit')


weights = {
        1: 0.5, 2: 1, 3: 1, 4: 1.5, 5: 2, 6: 2, 7: 1, 8: 2, 9: 1, 10: 1, 11: 0
    }


def evaluate_risk_aversion_from_form(form):
    scores = {'a': 1, 'b': 2, 'c': 3}
    total_score = 0
    for index in range(1, 12):  # Assuming you have 11 questions
        answer = getattr(form, f'question{index}').data
        if index == 11 and answer == 'b':
            return 50
        if index == 5 and answer == 'c':
            return 1  # Considered critical
        total_score += scores[answer] * weights[index]
    return total_score


def suggest_portfolio(score):
    max_score = sum(3 * weight for weight in weights.values())
    if score == 50:
        return "No Crypto"
    elif score == 1:
        return "Beginner"
    elif score <= max_score * 0.35:
        return "Very Conservative"
    elif score <= max_score * 0.4:
        return "Balanced"
    elif score <= max_score * 0.6:
        return "Growth"
    elif score <= max_score * 0.8:
        return "Growth"
    else:
        return "Very Dynamic"
