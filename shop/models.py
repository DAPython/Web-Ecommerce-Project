from flask_login import UserMixin
from shop import db


class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<AdminUser %r>' % self.username



class Product(db.Model):
    id_product = db.Column(db.Integer, primary_key=True)
    name_product = db.Column(db.String(120), unique=True, nullable=False)
    image_product = db.Column(db.String(120), unique=False, nullable=False)
    price = db.Column(db.String(120), unique=False, nullable=False)
    discount = db.Column(db.String(120), unique=False, nullable=False)
    description_product = db.Column(db.String(500), unique=False,
                     nullable=False)
    stock = db.Column(db.Integer, unique=False,
                     nullable=False)

    def __repr__(self):
        return '<Product %r>' % self.name_product
                     
class Category(db.Model):
    id_category = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(80), unique=True, nullable=False)
    image_category = db.Column(db.String(120), unique=False, nullable=False)
    description_category = db.Column(db.String(300), unique=False, nullable=False)

    def __repr__(self):
        return '<Category %r>' % self.name_category

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    role = db.Column(db.String(120), unique=False,
                     nullable=False, default='customer')

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()