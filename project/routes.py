from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from PIL import Image
import secrets
import os
from project import app, db, bcrypt, mail
from project.forms import AdminHomeForm, AdminLoginForm, RegistrationForm, LoginForm, UpdateAccountForm, UploadBookForm, RequestResetForm, ResetPasswordForm
from project.models import User, Books_list
from flask_mail import Message


@app.route('/')
def logo():
    return render_template('logo.html')    


@app.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    books = Books_list.query.order_by(Books_list.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', title='home', books=books)


@app.route('/login', methods=['Get', 'Post'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            other_page=request.args.get('next')
            return redirect(other_page) if other_page else redirect(url_for('home'))
        
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='login', form=form)

@app.route('/Adminlogin', methods=['Get', 'Post'])
def Adminlogin():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
            return redirect(url_for('Adminhome'))
    return render_template('Adminlogin.html', title='Adminlogin', form=form)

@app.route('/Adminhome', methods=['Get', 'Post'])
def Adminhome():
    form = AdminHomeForm()
    if form.validate_on_submit():
        db.session.delete(User.query.filter_by(username=form.username.data).one())
        db.session.commit()
        flash('User account has been deleted', 'success')
        return redirect(url_for('Adminhome'))
    return render_template('Adminhome.html', title='Adminhome', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.add(User(username=form.username.data, email=form.email.data, password=hashed_password))
        db.session.commit()
        flash('Your account is created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logo'))


def change_pic(update_picture):
    hex = secrets.token_hex(8)   # generates hexadecimal no of image
    _, extension = os.path.splitext(update_picture.filename)   # this returns 2 value name and extension of file
    picture_fn = hex + extension
    path = os.path.join(app.root_path, 'static/profile_pic', picture_fn) # saving image on a path

    output_size = (125, 125)          # resize the large image to small
    i = Image.open(update_picture)
    i.thumbnail(output_size)
    i.save(path)

    return picture_fn


@app.route('/account', methods=['Get', 'Post'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = change_pic(form.picture.data)
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
        db.session.add(Books_list(book_name=form.bookname.data,
                    semester=form.semester.data, price=form.price.data, 
                    phone=form.phone.data, owner=current_user))
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
        book.book_name = form.bookname.data
        book.semester = form.semester.data
        book.price = form.price.data
        book.phone = form.phone.data
        db.session.commit()
        flash('book updation has been done', 'success')
        return redirect(url_for('home', user_id=book.id))

    elif request.method == 'GET':
        form.bookname.data = book.book_name
        form.semester.data = book.semester
        form.price.data = book.price
        form.phone.data = book.phone
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

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                sender='noreply@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}
Ignore this message if request is not made by you.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        send_reset_email(User.query.filter_by(email=form.email.data).first())
        flash('email has been sent to registered email_id', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This link has been expired', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)