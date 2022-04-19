from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# mysql://root:root@localhost/notebook 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tparlisdlxurdz:ea35bd90e87172065f3f49525eadb16fda5808372caf8db50987ad1ebaddf81e@ec2-3-230-122-20.compute-1.amazonaws.com:5432/d5i3qv074m1dmh'
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app) # login manager contains the code that lets your application and Flask-Login work together, 
                                    # such as how to load a user from an ID, 
                                    # where to send users when they need to log in
login_manager.init_app(app)
login_manager.login_view = "login"                    # if user tries to route homepage w/o logging in it redirect user to login page
login_manager.login_message_category = 'info'         # setting message category
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'     # its loaction of mail server eg- gmail, yahoo, etc
app.config['MAIL_PORT'] = 587                         # port from email is sent to server
app.config['MAIL_USE_TLS'] = True                     # security encryption purpose 
app.config['MAIL_USERNAME'] = 'vipulvishwakarma111@gmail.com'
app.config['MAIL_PASSWORD'] = 'azbhdhmliyyoqabo'


db = SQLAlchemy(app)                                  # creating instance of database
bcrypt = Bcrypt(app)                                  # 
mail = Mail(app)


from project import routes


