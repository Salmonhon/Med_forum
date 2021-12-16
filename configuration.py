
from flask import Flask
from flask_sqlalchemy import  SQLAlchemy
from flask_mail import Mail
from flask_babel import Babel, _

app = Flask(__name__)
app.config['SECRET_KEY'] = 'salmonhon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'medforum039@gmail.com'  # for details open Lec23 slide 10
app.config['MAIL_PASSWORD'] = 'plzmqtfxrrrcrftq'  # for details open Lec23 slide 10
app.config['MAIL_DEFAULT_SENDER'] = 'medforum039@gmail.com'  # optional

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {'ru':'Russian', 'en':'English'}

babel = Babel(app)
mail = Mail(app)
db = SQLAlchemy(app)
