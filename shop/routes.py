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
    CountCart, totalPrice = getLoginDetails()
    with sqlite3.connect('shop/database.db') as conn:
        cur = conn.cursor()  
        cur.execute('SELECT id_category, name_category, image_category FROM category')
        myCategory = cur.fetchall()
        cur.execute('SELECT id_product, name_product, image_product, price FROM product')
        itemData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('index.html', myCategory=myCategory, itemData=itemData, CountCart=CountCart, totalPrice=totalPrice)

def getLoginDetails():
    if current_user.is_authenticated:
        id = current_user.id
        with sqlite3.connect('shop/database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(id_product) FROM cart WHERE id =" + str(id))
            CountCart = cur.fetchone()[0]
            cur.execute("SELECT product.id_product, product.name_product, product.image_product, product.price FROM product, cart WHERE product.id_product = cart.id_product AND cart.id = " + str(id))
            product = cur.fetchall()
        totalPrice = 0
        for row in product:
            totalPrice += row[3]
        conn.close()
        return (CountCart, totalPrice)

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
        cur.execute('SELECT product.id_product, product.name_product, product.image_product, product.price, product.discount, product.description_product, product.stock, category.name_category FROM product, category WHERE product.id_category = category.id_category and id_product =' + id_product)
        productData = cur.fetchone()
    conn.close()
    return render_template("product-description.html", data=productData)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route("/addToCart")
def addToCart():
    if current_user.is_authenticated:
        id_product = int(request.args.get('id_product'))
        with sqlite3.connect('shop/database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + session['email'] + "'")
            id_user = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO cart(id, id_product) VALUES (?,?)", (id_user, id_product))
                conn.commit()
            except:
                conn.rollback()
        conn.close()
        return redirect(url_for('kart'))
    else:
        return redirect(url_for('login'))


@app.route("/kart")
def kart():
    
    if current_user.is_authenticated:
        id = current_user.id
        with sqlite3.connect('shop/database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT product.id_product, product.name_product, product.image_product, product.price FROM product, cart WHERE product.id_product = cart.id_product AND cart.id = " + str(id) + " GROUP BY product.id_product")
            product = cur.fetchall()
        quantity = 0
        for row in product:
            quantity += row[0]
        totalPrice = 0
        for row in product:
            totalPrice += row[3]
        return render_template("cart.html", product = product, totalPrice=totalPrice, quantity=quantity)
    else:
        return redirect(url_for('login'))

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    id_product = int(request.args.get('id_product'))
    with sqlite3.connect('shop/database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM user WHERE email = '" + email + "'")
        id_user = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM cart WHERE id = " + str(id_user) + " AND id_product = " + str(id_product))
            conn.commit()
        except:
            conn.rollback()
    conn.close()
    return redirect(url_for('kart'))



    



