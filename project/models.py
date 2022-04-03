from datetime import datetime
from project import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),nullable=False, unique=True)
    email = db.Column(db.String(120),nullable=False, unique=True)
    image_file = db.Column(db.String(200), nullable=False, default='account.jpg')
    password = db.Column(db.String(200), nullable=False)
    books = db.relationship('Books_list', backref='owner', lazy=True)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}')"


class Books_list(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(80), nullable=False)
    book_img = db.Column(db.String(200), nullable=False, default='book.png')
    semester = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Books_list('{self.book_name}', '{self.book_img}', '{self.date_posted}')"

# db.drop_all()
# db.create_all()
