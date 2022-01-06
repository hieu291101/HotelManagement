from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_babelex import Babel
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "819048&(*%^*(*&(@9789&^&()(!@#$"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:281001@localhost/quanlykhachsandb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app=app)

admin = Admin(app=app, name='Hotel Management', template_mode='bootstrap4')

login = LoginManager(app=app)

babel = Babel(app=app)


@babel.localeselector
def get_locale():
    return 'vi'
