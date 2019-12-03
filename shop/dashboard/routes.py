from flask import render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from shop.models import Product, User, Category
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators
from shop import app, db, bcrypt
import sqlite3
import os


class Categories(Form):
    name_category = StringField('Name', [validators.DataRequired()])
    image_category = StringField('Image', [validators.DataRequired()])
    description_category = StringField(
        'Description', [validators.DataRequired()])




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
   if request.method == "POST":
      name = request.form['name']
      image = request.form['image']
      des = request.form['description']
      with sqlite3.connect('shop/database.db') as con:
         try:
            cur = con.cursor()
            cur.execute('INSERT INTO category(name_category, image_category, description_category) VALUES (?,?,?)', (name, image, des))
            con.commit()
         except:
            con.rollback()
      con.close()
   return render_template('dashboard/addcategory.html')

@app.route('/removecategory')
def removecategory():
   id_category = request.args.get('id_category')
   with sqlite3.connect('shop/database.db') as conn:
      try:
         cur = conn.cursor()
         cur.execute('DELETE FROM category WHERE id_category = ' +  id_category)
         conn.commit()
      except:
         conn.rollback()
   conn.close()
   return redirect(url_for('category'))


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
   if request.method == "POST":
      name = request.form['name']
      image = request.form['image']
      price = request.form['price']
      discount = request.form['discount']
      des = request.form['description']
      stock = request.form['stock']
      with sqlite3.connect('shop/database.db') as con:
         try:
            cur = con.cursor()
            cur.execute('INSERT INTO product(name_product, image_product, price, discount, description_product, stock) VALUES (?,?,?,?,?,?)', (name, image, price, discount, des, stock))
            con.commit()
         except:
            con.rollback()
      con.close()
   return render_template('dashboard/addproduct.html')

@app.route('/removeproduct')
def removeproduct():
   id_product = request.args.get('id_product')
   with sqlite3.connect('shop/database.db') as conn:
      try:
         cur = conn.cursor()
         cur.execute('DELETE FROM product WHERE id_product = ' +  id_product)
         conn.commit()
      except:
         conn.rollback()
   conn.close()
   return redirect(url_for('product'))


@app.route('/removeuser')
def removeuser():
   id = request.args.get('id')
   with sqlite3.connect('shop/database.db') as conn:
      try:
         cur = conn.cursor()
         cur.execute('DELETE FROM user WHERE id = ' +  id)
         conn.commit()
      except:
         conn.rollback()
   conn.close()
   return redirect(url_for('user'))

@app.route('/user')
def user():
    user = User.query.all()
    return render_template('dashboard/user.html', user=user)

@app.route('/edituser', methods=['POST', 'GET'])
def edituser():
   id = request.args.get('id')
   with sqlite3.connect('shop/database.db') as conn:
      cur = conn.cursor()
      user = cur.execute('SELECT * FROM user WHERE id=' + id)
   return render_template('dashboard/edituser.html', user=user)

@app.route('/updateuser')
def updateuser():
   id = request.args.get('id')
   if request.method == "POST":
      username= request.form['username']
      password = request.form['password']
      role = request.form['role']
      with sqlite3.connect('shop/database.db') as conn:
         try:
            cur.execute('UPDATE user SET username=' + username + ', password=' + password + ', role=' + role + ' WHERE id=' + id)
            conn.commit()
         except:
            conn.rollback()
      conn.close()
   return redirect(url_for(user))

@app.route('/category')
def category():
    category = Category.query.all()
    return render_template('dashboard/category.html', category=category)


@app.route('/product')
def product():
    product = Product.query.all()
    return render_template('dashboard/product.html', product=product, title='Product | Admin')



