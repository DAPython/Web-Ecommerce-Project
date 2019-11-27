from flask import render_template, session, request, redirect, url_for, flash
import sqlite3, os
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import InputRequired, Email, Length
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from .dashboard import routes
from .models import User, AdminUser, Product, Category
from shop import app, db, bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class LoginForm(Form):
   email = StringField('Email Address', [validators.Length(min=6, max=35)])
   password = PasswordField('Password', [validators.DataRequired()])




class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')



db.create_all()

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(AdminUser, db.session))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    myCategory = Category.query.all()
    with sqlite3.connect('shop/database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id_product, name_product, image_product, price FROM product')
        itemData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('index.html', myCategory=myCategory, itemData=itemData)

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(5):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

def removeLineBreaks(text) :
    newText = ''
    for char in text:
        if char == '\r\n' or char == '\r' or char == '\n':
            newText += '\\n'
        else:
            newText += char
    return newText

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.role == 'admin':
                session['email'] = form.email.data
                login_user(user)
                flash(f'Welcome {form.email.data}')
                return redirect(request.args.get('next') or url_for('dashboard'))
            else:
                session['email'] = form.email.data
                login_user(user)
                flash(f'Welcome {form.email.data}')
                return redirect(request.args.get('next') or url_for('index'))
        else:
            flash(f'Wrong')
    return render_template('login.html', form = form)


@app.route("/logout")
@login_required
def logout():
    session.pop('email', None)
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Thanks {form.username.data} for registering')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/productdescription')
def productdescription():
    id_product = request.args.get('id_product')
    with sqlite3.connect('shop/database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id_product, name_product, image_product, price, discount, description_product, stock FROM product WHERE id_product =' + id_product)
        productData = cur.fetchone()
    conn.close()
    return render_template("product-description.html", data=productData)




    



