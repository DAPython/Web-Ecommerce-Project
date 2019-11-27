from flask import render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from shop.models import Product, User, Category
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators
from shop import app, db, bcrypt
import sqlite3, os


class Categories(Form):
    name_category = StringField('Name', [validators.DataRequired()])
    image_category = StringField('Image', [validators.DataRequired()])
    description_category = StringField('Description', [validators.DataRequired()])


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated and current_user.role != 'admin':
       return redirect(url_for('index'))
    return render_template('dashboard/index.html')

@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
   form = Categories(request.form)
   if request.method == "POST":
      name = form.name_category.data
      image = form.image_category.data
      des = form.description_category.data
      cat = Categories(name_category=name, image_category=image, description_category=des)
      db.session.add(cat)
      db.session.commit()
      flash(f'The category was added!')
      return redirect(url_for('dashboard'))
   return render_template('dashboard/category.html', form=form)


@app.route('/user')
def user():
   user = User.query.all()
   return render_template('dashboard/user.html', user=user)

@app.route('/product')
def product():
   title = 'Product | Admin'
   product = Product.query.all()
   return render_template('dashboard/product.html', product=product, title=title)



