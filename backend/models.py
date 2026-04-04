from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Store(db.Model):
    __tablename__ = "stores"
    store_id = db.Column(db.String(20), primary_key=True)
    store_name = db.Column(db.String(120), nullable=False)

class Colleague(db.Model):
    __tablename__ = "colleagues"
    colleague_id = db.Column(db.String(20), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(50), nullable=False, default="colleague")
    colleague_since = db.Column(db.String(20), nullable=True)  # "MM/YYYY"
    store_id = db.Column(db.String(20), db.ForeignKey("stores.store_id"), nullable=False)
    first_name = db.Column(db.String(50), nullable=False, default="")
    last_name = db.Column(db.String(50), nullable=False, default="")
    position = db.Column(db.String(60), nullable=False, default="")

class Product(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.String(32), primary_key=True)  # UPC/barcode
    product_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=0)      # max shelf capacity
    tray_size = db.Column(db.Integer, nullable=False, default=1)     # items per delivered box/tray

class StoreStock(db.Model):
    __tablename__ = "store_stock"
    store_id = db.Column(db.String(20), db.ForeignKey("stores.store_id"), primary_key=True)
    product_id = db.Column(db.String(32), db.ForeignKey("products.product_id"), primary_key=True)
    stock_amount = db.Column(db.Integer, nullable=False, default=0)

class GapScanSession(db.Model):
    __tablename__ = "gap_scan_sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Session ID
    store_id = db.Column(db.String(20), db.ForeignKey("stores.store_id"), nullable=False)
    submitted_by = db.Column(db.String(20), nullable=False)  # colleague_id (string)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Accuracy-check locking to prevent 2 people doing the same session
    status = db.Column(db.String(20), nullable=False, default="submitted")  # submitted / in_progress / completed
    claimed_by = db.Column(db.String(20), nullable=True)
    claimed_at = db.Column(db.DateTime, nullable=True)

    completed_at = db.Column(db.DateTime, nullable=True)


class GapScanItem(db.Model):
    __tablename__ = "gap_scan_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey("gap_scan_sessions.id"), nullable=False)
    product_id = db.Column(db.String(32), db.ForeignKey("products.product_id"), nullable=False)

    # If found backstage during accuracy check, mark found and exclude from zeroing
    found_backstage = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.UniqueConstraint("session_id", "product_id", name="uq_gap_session_product"),
    )

class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.String(20), db.ForeignKey("stores.store_id"), nullable=False)

    requested_by = db.Column(db.String(20), nullable=False)   # colleague_id
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    status = db.Column(db.String(20), nullable=False, default="requested")
    # requested -> fulfilled -> processed
    fulfilled_at = db.Column(db.DateTime, nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)

    barcode_code = db.Column(db.String(64), nullable=True)  # STOREID-DELIVERYID-XXXXX


class DeliveryItem(db.Model):
    __tablename__ = "delivery_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey("deliveries.id"), nullable=False)
    product_id = db.Column(db.String(32), db.ForeignKey("products.product_id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint("delivery_id", "product_id", name="uq_delivery_product"),
    )