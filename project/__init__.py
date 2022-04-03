from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# mysql://root:root@localhost/notebook 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tparlisdlxurdz:ea35bd90e87172065f3f49525eadb16fda5808372caf8db50987ad1ebaddf81e@ec2-3-230-122-20.compute-1.amazonaws.com:5432/d5i3qv074m1dmh'
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'     #its loaction of mail server eg- gmail, yahoo, etc
app.config['MAIL_PORT'] = 587                         # port from email is sent to server
app.config['MAIL_USE_TLS'] = True                     # security encryption purpose 
app.config['MAIL_USERNAME'] = 'vipulvishwakarma111@gmail.com'
app.config['MAIL_PASSWORD'] = 'azbhdhmliyyoqabo'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)


from project import routes


