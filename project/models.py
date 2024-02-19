import datetime

from sqlalchemy import func

from project import db, login_manager
from project import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    _password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    picprofile = db.Column(db.String(255), nullable=True)

    @property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plain_text_password):
        self._password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self._password_hash, attempted_password)


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    list_selected_assets = db.Column(db.Text, nullable=False)  # JSON serialized list
    list_weight_selected_assets = db.Column(db.Text, nullable=False)  # JSON serialized list
    data_portfolio = db.Column(db.Text, nullable=False)  # JSON serialized data
    is_invested = db.Column(db.Boolean, default=False, nullable=False)
    capital = db.Column(db.Integer, nullable=False)
    horizon = db.Column(db.Integer, nullable=False)
    user = db.relationship('users', backref=db.backref('portfolio', lazy=True))
    future_value = db.Column(db.Integer, nullable=False)
    list_plotdata = db.Column(db.Text, nullable=False)
    assets_info = db.Column(db.String(255), nullable=False)




    def __repr__(self):
        return f'<Portfolio {self.name}>'