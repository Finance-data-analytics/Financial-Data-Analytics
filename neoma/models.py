from neoma import db, login_manager
from neoma import bcrypt
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
    idpf = db.Column(db.Integer, nullable=True)
    picprofile = db.Column(db.String(255), nullable=True)

    @property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plain_text_password):
        self._password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self._password_hash, attempted_password)
