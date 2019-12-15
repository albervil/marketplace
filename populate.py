from app import db, bcrypt
import src.models as models

import json

def populatedb():
    if models.User.query.count() == 0:
        print("Importing users...")
        with open('resources/users.json') as f:
            user_list = json.load(f)
            for u in user_list:
                pw_hash = bcrypt.generate_password_hash(u['password']).decode('utf-8')
                usr = models.User(u['email'], pw_hash, u['country'], u['currency'])
                db.session.add(usr)
            db.session.commit()

    if db.session.query(models.Product).count() == 0:
        print("Importing products...")
        with open('resources/products.json') as f:
            product_list = json.load(f)
            for p in product_list:
                prod = models.Product(p['user'], p['description'], p['price'])
                db.session.add(prod)
            db.session.commit()