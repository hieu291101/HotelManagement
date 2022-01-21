from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_babelex import Babel
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = "819048&(*%^*(*&(@9789&^&()(!@#$"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tinhyeulathe1@localhost/quanlykhachsandb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4
app.config['PAGE_SIZE_ROOM_ORDER'] = 6

db = SQLAlchemy(app=app)

admin = Admin(app=app, name='Hotel App', template_mode='bootstrap4')

login = LoginManager(app=app)

babel = Babel(app=app)

cloudinary.config(
    cloud_name="dinhnguyenthanh",
    api_key="695521882677629",
    api_secret="TcLlKGeCuAhiGMqa_DzajlI_z8U"
)

@babel.localeselector
def get_locale():
    return 'vi'
