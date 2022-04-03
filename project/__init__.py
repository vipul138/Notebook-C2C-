from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

#  postgresql://cjzkpjkvfmxwuj:e62e25c0b11f855a085e46867c5a6c2aee392922de43dcdd2a2cf1bb9a994cf6@ec2-3-218-171-44.compute-1.amazonaws.com:5432/dac10m6lfngorp
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/notebook'
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



from project import routes


