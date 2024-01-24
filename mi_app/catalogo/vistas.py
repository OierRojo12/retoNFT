from flask  import request, jsonify, Blueprint
from mi_app import db, login_manager
from mi_app.catalogo.modelos import Product, Category, User
from mi_app.catalogo.modelos import ProductForm, LoginForm, RegistrationForm
from flask import render_template
from flask import flash
from flask import redirect, url_for
from flask_login import current_user, login_user, logout_user, \
    login_required

import json, requests
from flask_restful import Resource, reqparse, abort
from mi_app import api

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('price', type=float)
#parser.add_argument('category', type=dict)
parser.add_argument('category', type=str)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

catalog = Blueprint('catalog',__name__)

'''
Esto es or una duda que me preguntó Efren
@catalog.route('/one-request')
def request_one():
    prod = request.args.get('silla', 'producto')    
    return f'A simple Flask request where argument is {prod}'
# ejemplo url: http://127.0.0.1:5000/one-request?silla=taburete
# resultado: 'A simple Flask request where argument is taburete'

@catalog.route('/one-request/<silla>')
def request_two(silla):
    return f'A simple Flask request where argument is {silla}'
# ejemplo url: http://127.0.0.1:5000/one-request/taburete
# resultado: 'A simple Flask request where argument is taburete'
'''

@catalog.route('/')
@catalog.route('/home')
def home():
    return render_template('home.html')


@catalog.route('/product/<int:id>')
@login_required
def product(id):
    miurl = 'http://127.0.0.1:5000' + url_for('productoapi', id=id)
    print('miurl:', miurl)
    response = requests.get(miurl)
    producto = json.loads(response.text)
    #print('tipo PRODUCTO:', type(producto))
    #print('PRODUCTO:', producto)
        
    return render_template('producto.html', product=producto[f'{id}'])


@catalog.route('/products')
@catalog.route('/products/<int:page>')
@login_required
def products(page=1):
    # products = Product.query.paginate(page=page, per_page=6)
    miurl = 'http://127.0.0.1:5000' + url_for('productoapi', page=page)
    print('miurl:', miurl)
    response = requests.get(miurl)
    # print('response.text:', response.text)
    products = json.loads(response.text)
    print('tipo PRODUCTO:', type(products))
    print('PRODUCTOS:', products)
    return render_template('products.html', products=products)
    #products = Product.query.all()
    #products = Product.query.paginate(page=page, per_page=10).items    
    '''res = {}
    for product in products:
        res[product.id] = {
            'name': product.name,
            'price': str(product.price),
            'category': product.category.name
        }
    return jsonify(res)'''

# De momento enrutar aquí el link de uno de los productos, para probar
# Habrá que hacer un nuevo botón al lado del producto hacia formulario de cambio.
@catalog.route('/product-change/<int:id>', methods=['GET'])
@login_required
def change_product(id):
    # pongo datos a mano, debería recogerlos del formulario
    name = 'mesa_nueva'
    price = 235
    category = 'muebles1' # debe ser una de las existentes en la BD
    d = {'name': name, 'price': price, 'category': category}
    miurl = 'http://127.0.0.1:5000' + url_for('productoapi', id=id)
    print('miurl_PUT:', miurl)
    response = requests.put(miurl, data=json.dumps(d), headers={'Content-Type': 'application/json'})
    # response = requests.get(miurl)    
    producto = json.loads(response.text)
    print('PRODUCTO DEVUELTO', producto)
    return redirect(url_for('catalog.product', id=id))

@catalog.route('/product-create', methods=['GET','POST'])
@login_required
def create_product():
    form = ProductForm(meta={'csrf': False})
    categories = [(c.id, c.name) for c in Category.query.all()]
    form.category.choices = categories
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        category = Category.query.get_or_404(form.category.data)        
        product = Product(name, price, category)
        db.session.add(product)
        db.session.commit()
        flash(f'The product {name} has been created', 'success')
        return redirect(url_for('catalog.product', id=product.id))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('crear_producto.html', form=form)
    '''name = request.form.get('name')
    price = request.form.get('price')
    categName = request.form.get('category')
    category = Category.query.filter_by(name=categName).first()
    if not category:
        category = Category(categName)
    product = Product(name,price,category)    
    db.session.add(product)
    db.session.commit()
    #return 'Product created.'
    return render_template('producto.html', product=product)'''

@catalog.route('/category-create', methods=['GET'])
@login_required
def create_category():
    name = request.args.get('name')
    category = Category(name)
    db.session.add(category)
    db.session.commit()
    #return 'category created'
    return render_template('category.html', category=category)

@catalog.route('/category/<id>')
@login_required
def category(id):
    category = Category.query.get_or_404(id)
    return render_template('category.html', category=category)

@catalog.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)
    '''res = {}
    for category in categories:
        res[category.id] = {
            'name': category.name
        }
        res[category.id]['products']=[]
        for product in category.products:
            res[category.id]['products'].append({
                'id': product.id,
                'name': product.name,
                'price': product.price                
            })
    return jsonify(res)'''

@catalog.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('catalog.home'))

    form = LoginForm()
    # Si no ponemos form = LoginForm(meta={'csrf': False})
    # luego en los html habrá que añadir al formulario
    # {{ form.csrf_token }}

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()

        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)

        login_user(existing_user, remember=True)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('catalog.products'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)

@catalog.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Your are already logged in.', 'info')
        return redirect(url_for('catalog.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash(
                'This username has been already taken. Try another one.',
                'warning'
            )
            return render_template('register.html', form=form)
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered. Please login.', 'success')
        return redirect(url_for('catalog.login'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('register.html', form=form)

@catalog.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('catalog.home'))


class ProductoApi(Resource):    

    def get(self, id=None, page=1):
        if not id:
            print('PAGE:', page)
            products = Product.query.paginate(page=page, per_page=3)
        else:
            products = [Product.query.get(id)]
        if not products:
            abort(404)
        res = {}
        print('items object:', dir(products) )
        print('TIPO items :', type(products) )
        '''
        Enviar todos los items de una y manejarlos allí:
            'pageItems': products.items,
            'nextPage': products.next_num,
            'prevPage':products.prev_num
        '''                
        if type(products) is list:
            itemsAiterar = products
            hayItems = False
        else:
            itemsAiterar = products.items
            hayItems = True

        for product in itemsAiterar:            
            res[product.id] = {
                    'name': product.name,
                    'price': product.price,
                    'category': product.category.name                    
                }        
        
        if hayItems: 
            resp = {
            'pageItems': res,
            'nextPage': products.next_num,
            'prevPage': products.prev_num
            }
            return jsonify(resp)
        else: 
            return jsonify(res)        

    def post(self):
        args = parser.parse_args()
        name = args['name']
        price = args['price']
        categ_name = args['category']['name']
        category = Category.query.filter_by(name=categ_name).first()
        if not category:
            category = Category(categ_name)
        product = Product(name, price, category)
        db.session.add(product)
        db.session.commit()
        res = {}
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name
        }
        print('LO QUE DEVUELVE EL POST', res)
        return jsonify(res)

    def put(self, id):
        args = parser.parse_args()
        prodNname = args['name']
        prodPrice = args['price']
        categ_name = args['category']
        category = Category.query.filter_by(name=categ_name).first()
        Product.query.filter_by(id=id).update({
            'name': prodNname,
            'price': prodPrice,
            'category_id': category.id
        })        
        db.session.commit()
        product = Product.query.get_or_404(id)
        if product is None:
            return jsonify({'message': 'Category not found'}), 404
        res = {}
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name
        }
        print('LO QUE DEVUELVE EL PUT', res)
        return res

    def delete(self, id):
        product = Product.query.filter_by(id=id)
        product.delete()
        db.session.commit()
        return json.dumps({'response': 'Success'})

api.add_resource(
    ProductoApi,
    '/api/product',
    '/api/product/<int:id>',
    '/api/products/<int:page>'
)