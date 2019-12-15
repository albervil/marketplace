from app import db

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller = db.relationship('User', backref='products', lazy=True)
    likes = db.relationship('Like', backref='product', lazy=True)

    def __init__(self, user_id, description, price):
        self.user_id = user_id
        self.description = description
        self.price = price


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    pw_hash = db.Column(db.String, nullable=False)
    country = db.Column(db.String(2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)

    def __init__(self, email, pw_hash, country, currency):
        self.email = email
        self.pw_hash = pw_hash
        self.country = country
        self.currency = currency


class Like(db.Model):
    __tablename__ = 'like'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uix_1'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __init__(self, user_id, product_id):
        self.user_id = user_id
        self.product_id = product_id

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'product_id': self.product_id,
        }

    def __repr__(self):
        return json.dumps(self.to_dict())