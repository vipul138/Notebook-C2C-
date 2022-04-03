from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# mysql://root:root@localhost/notebook 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sxdhvypeupceuh:3fe03d3bcac07280528f7aaa5c8a5b0829fd10399767bfecf8facc7b460c047c@ec2-54-173-77-184.compute-1.amazonaws.com:5432/devsjed06efl05'
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'     #its loaction of mail server eg- gmail, yahoo, etc
app.config['MAIL_PORT'] = 587     # port from email is sent to server
app.config['MAIL_USE_TLS'] = True   # security encryption purpose 
app.config['MAIL_USERNAME'] = 'vipulvishwakarma111@gmail.com'
app.config['MAIL_PASSWORD'] = 'azbhdhmliyyoqabo'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

db.create_all()

from project import routes


