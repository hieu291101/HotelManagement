from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_babelex import Babel
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
import cloudinary

app = Flask(__name__)
app.secret_key = "819048&(*%^*(*&(@9789&^&()(!@#$"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:281001@localhost/quanlykhachsandb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4
app.config['PAGE_SIZE_ROOM_ORDER'] = 6

# Email related Configuration values
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'thanhdinhc2810@gmail.com'
app.config['MAIL_PASSWORD'] = 'dinhdeptrai2810'
app.config['MAIL_DEFAULT_SENDER'] = 'thanhdinhc2810@gmail.com'


db = SQLAlchemy(app=app)

admin = Admin(app=app, name='Hotel App', template_mode='bootstrap4')

login = LoginManager(app=app)

babel = Babel(app=app)

##########################
mail = Mail(app=app)
bcrypt = Bcrypt(app=app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'


cloudinary.config(
    cloud_name="dinhnguyenthanh",
    api_key="695521882677629",
    api_secret="TcLlKGeCuAhiGMqa_DzajlI_z8U"
)


@babel.localeselector
def get_locale():
    return 'vi'
