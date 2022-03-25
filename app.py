from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, redirect, request, flash, abort
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from PIL import Image
import secrets
import os, re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/notebook'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info'


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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Books_list('{self.book_name}', '{self.book_img}', '{self.date_posted}')"


class RegistrationForm(FlaskForm):
    # id = IntegerField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
    

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(validators=[DataRequired(), Email()])
    picture = FileField('update picture',validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class UploadBookForm(FlaskForm):
    bookname = StringField(validators=[DataRequired()])
    # bookimg =  FileField('upload img',validators=[FileAllowed(['jpg', 'png'])])
    semester = SelectField(choices = [('1', '1 Sem'), ('2', '2 Sem'), ('3', '3 Sem'), 
                                        ('4', '4 Sem'), ('5', '5 Sem'), ('6', '6 Sem')])
    price = IntegerField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Upload')

    def validate_phone(self, phone):
        pattern = re.compile("[7-9][0-9]{9}")
        if pattern.match(phone.data):
            pass
        else:
            raise ValidationError("enter correct number")


@app.route('/')
def logo():
    return render_template('logo.html')    


@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    books = Books_list.query.order_by(Books_list.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', title='home', books=books)


@app.route('/login', methods=['Get', 'Post'])
def login():
    form=LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            other_page=request.args.get('next')
            return redirect(other_page) if other_page else redirect(url_for('home'))
        
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='login', form=form)

 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logo'))


def save_pic(form_picture):
    random_hex = secrets.token_hex(8)   # generates hexadecimal no of image
    _, f_ext = os.path.splitext(form_picture.filename)   # this returns 2 value name and extension of file
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pic', picture_fn) # saving image on a path

    output_size = (125,125)          # resize the large image to small
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# def save_book(form_bookimg):
#     random_hex = secrets.token_hex(8)   # generates hexadecimal no of image
#     _, f_ext = os.path.splitext(form_bookimg.filename)   # this returns 2 value name and extension of file
#     bookimg_fn = random_hex + f_ext
#     bookimg_path = os.path.join(app.root_path,'static/image', bookimg_fn) # saving image on a path
    
#     output_size = (125,125)          # resize the large image to small 
#     i = Image.open(form_bookimg)
#     i.thumbnail(output_size)
#     i.save(bookimg_path)

#     return bookimg_fn 


@app.route('/account', methods=['Get', 'Post'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_pic(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('account'))

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file=url_for('static', filename='profile_pic/' + current_user.image_file)
    return render_template('account.html', title='account', image_file=image_file, form=form)


@app.route('/sellbook', methods=['Get', 'Post'] )
@login_required
def sellbook():
    form = UploadBookForm()
    if form.validate_on_submit():
        upload = Books_list(book_name=form.bookname.data,
                    semester=form.semester.data, price=form.price.data, 
                    phone=form.phone.data, owner=current_user)
        db.session.add(upload)
        db.session.commit()
        return redirect(url_for('home'))
        
    return render_template('sellbook.html', title='sellbook', form=form, legend='Upload book')



@app.route("/book/<int:user_id>")
def book(user_id):
    book = Books_list.query.get_or_404(user_id)
    return render_template('book.html', title=book.owner.username, book=book)


@app.route('/book/<int:user_id>/update', methods=['Get', 'Post'] )
@login_required
def update_book(user_id):
    book = Books_list.query.get_or_404(user_id)
    if book.owner != current_user:
        abort(403)
    form = UploadBookForm()
    if form.validate_on_submit():
        book.book_name=form.bookname.data
        book.semester=form.semester.data
        book.price=form.price.data
        book.phone=form.phone.data
        db.session.commit()
        flash('book updation has been done', 'success')
        return redirect(url_for('home', user_id=book.id))

    elif request.method == 'GET':
        form.bookname.data=book.book_name
        form.semester.data=book.semester
        form.price.data=book.price
        form.phone.data=book.phone
    return render_template('sellbook.html', title='update book', form=form, legend='Update Book')



@app.route('/book/<int:user_id>/delete', methods=['Get', 'Post'] )
@login_required
def delete_book(user_id):
    book = Books_list.query.get_or_404(user_id)
    if book.owner != current_user:
        abort(403)
    db.session.delete(book)
    db.session.commit()
    flash('Your book has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_book(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    books = Books_list.query.filter_by(owner=user)\
                .order_by(Books_list.date_posted.desc())\
                .paginate(page=page, per_page=4)
    return render_template('user_book.html', title='userBook',books=books, user=user)


if __name__ == '__main__':
    app.run(debug=True)


