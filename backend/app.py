from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Store, Colleague
from werkzeug.security import check_password_hash
from models import db, Store, Colleague, Product, StoreStock

import jwt, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SECRET_KEY'] = 'dev-secret-key'
CORS(app)
db.init_app(app)

@app.route('/api/stores', methods=['GET'])
def get_stores():
    stores = Store.query.all()
    return jsonify([{'id': s.store_id, 'name': s.store_name} for s in stores])

@app.route('/api/store/<store_id>', methods=['GET'])
def get_store(store_id):
    s = Store.query.filter_by(store_id=store_id.upper()).first()
    if not s:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': s.store_id, 'name': s.store_name})

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate a colleague and return a signed JWT token."""
    data = request.get_json()
    colleague_id = data.get('colleague_id', '')
    password = data.get('password', '')
    # look up the colleague record in the database
    colleague = Colleague.query.filter_by(colleague_id=colleague_id).first()
    # check_password_hash compares the plaintext against the stored hash
    if not colleague or not check_password_hash(colleague.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    # build the JWT payload - exp sets the expiry to 8 hours from now
    token = jwt.encode({
        'sub': colleague_id,
        'name': colleague.first_name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'name': colleague.first_name})


# ── Stage 3: product lookup ────────────────────────────────────────────

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Return product details for a given barcode. ?store_id= for stock."""
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    store_id = request.args.get('store_id', '').strip()
    stock_amount = 0
    if store_id:
        row = StoreStock.query.filter_by(
            store_id=store_id, product_id=product.product_id).first()
        stock_amount = row.stock_amount if row else 0
    return jsonify({
        'product_id': product.product_id,
        'product_name': product.product_name,
        'price': product.price,
        'capacity': product.capacity,
        'tray_size': product.tray_size,
        'stock_amount': stock_amount
    })

# Stage 4

@app.route('/api/waste', methods=['POST'])
def waste():
    # Records waste event which subtracts qty from the store's stock level
    data       = request.json or {}
    store_id   = (data.get('store_id') or '').strip()
    product_id = (data.get('product_id') or '').strip()
    qty        = data.get('qty')

    # Checking for empty fields to avoid errors
    if not store_id or not product_id or qty is None:
        return jsonify({'error': 'Missing fields'}), 400

    try: # checks if qty is an integer
        qty = int(qty)
    except (ValueError, TypeError):
        return jsonify({'error': 'qty must be integer'}), 400
    
    product = Product.query.filter_by(product_id=product_id).first()
    if not product: # checks product exists in database
        return jsonify({'error': 'Product not found'}), 404

    # Checks current stock level for the product
    row = StoreStock.query.filter_by(
        store_id=store_id, product_id=product_id).first()
    if not row:
        row = StoreStock(store_id=store_id, product_id=product_id,
                         stock_amount=0)
        db.session.add(row)

    # Subtracts qty from the stock level
    row.stock_amount = int(row.stock_amount) - qty
    db.session.commit() # Commits the new quantity to the database
    return jsonify({'ok': True, 'new_stock_amount': row.stock_amount})

@app.route('/api/stockcount', methods=['POST'])
def stockcount():
    '''Set stock_amount to the provided count total. REPLACES existing value.'''
    data     = request.json or {}
    store_id = (data.get('store_id') or '').strip()
    items    = data.get('items', [])
    if not store_id or not isinstance(items, list):
        return jsonify({'error': 'Invalid payload'}), 400
    for it in items:
        pid   = (it.get('product_id') or '').strip()
        total = it.get('total')
        if not pid or total is None:
            return jsonify({'error': 'Missing fields'}), 400
        try:
            total = int(total)
        except (ValueError, TypeError):
            return jsonify({'error': 'total must be integer'}), 400
        if not Product.query.filter_by(product_id=pid).first():
            return jsonify({'error': f'Product not found: {pid}'}), 404
        row = StoreStock.query.filter_by(
            store_id=store_id, product_id=pid).first()
        if not row:
            row = StoreStock(store_id=store_id, product_id=pid,
                             stock_amount=total)
            db.session.add(row)
        else:
            row.stock_amount = total   # REPLACE not increment
    db.session.commit()
    return jsonify({'ok': True})



if __name__ == '__main__':
    app.run(debug=True, port=5000)
