from mi_app import db
from wtforms import StringField, DecimalField, SelectField, PasswordField
from flask_wtf import FlaskForm
from decimal import Decimal
from wtforms.validators import InputRequired, NumberRange, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Product(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(
        'Category', backref=db.backref('products', lazy='dynamic')
    )
    # category será el atributo de relación para poder acceder a la
    # categoría de un producto mediante 'product.category'
    '''
    db.relationship crea una relación entre la clase Product y la clase 
    Category. Establece un vínculo entre las instancias de estas dos clases
    en el modelo de SQLAlchemy.
    --
    Si tenemos una instancia de Category, podemos acceder a sus productos 
    relacionados mediante category.products. Al ser la relación bidireccional,
    también podremos acceder a product.category 
    ---
    lazy='dynamic' define la estrategia de carga para la relación inversa. 
    En este caso, se establece en 'dynamic', lo que significa que la relación 
    inversa devolverá un objeto de consulta que permite realizar más filtrados 
    de resultados.    
    '''
    
    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category
    def __repr__(self):
        return f'<Product {self.id}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Category {self.id}>'

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    price = DecimalField('Price', validators=[
        InputRequired(), NumberRange(min=Decimal('0.0'))
    ])
    category = SelectField(
        'Category', validators=[InputRequired()], coerce=int
    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    pwdhash = db.Column(db.String())
 
    def __init__(self, username, password):
        self.username = username
        self.pwdhash = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

class RegistrationForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField(
        'Password', [
            InputRequired(), EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Confirm Password', [InputRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])