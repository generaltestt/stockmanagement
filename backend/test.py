from models import Store
from app import app, db
with app.app_context():
    db.session.add(Store(store_id='0725', store_name='M&S Islington'))
    db.session.add(Store(store_id='0123', store_name='M&S Enfield'))
    db.session.add(Store(store_id='HO',   store_name='Head Office'))