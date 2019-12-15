import json
from src.exception.restrictions import LikeOwnItemException
from src.services.currency_conversion_service import convert
from sqlalchemy.exc import IntegrityError
from src.models import Product, User, Like

def feed(user, filters, sorting):
    products = Product.query.join(User).filter(Product.user_id != user.id)

    if filters['country']:
        products = products.filter(User.country == filters['country'])

    feed = [
        extend(product, user) for product in products.all() \
        if pass_price_filters(extend(product, user), filters)
    ]

    sort_field = sorting['sort']

    if sorting['sort']:
        desc_sort = sorting['order'] is not None and sorting['order'] == 'DESC'
        return sorted(feed, key=lambda prod: prod[sort_field], reverse=desc_sort)
    else:
        return feed

def get(user, id):
    product = Product.query.get(id)

    if product is None:
        return None
    else:
        return extend(product, user)

def like(user, id):
    from src.models import db

    product = Product.query.get(id)

    if product is None:
        return None

    if user.id == product.user_id:
        raise LikeOwnItemException()

    lk = Like(user.id, id)
    try:
        db.session.add(lk)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return get(user, id)


def extend(product, buyer):
    price = product.price if buyer.currency == product.seller.currency \
                    else convert(
                        product.price, product.seller.currency, buyer.currency
                    )
    return {
        'id': product.id,
        'user_id': product.user_id,
        'description': product.description,
        'country': product.seller.country,
        'price': price,
        'likes': len(product.likes)
    }

def pass_price_filters(product, filters):
    if filters['min_price'] and product['price'] < filters['min_price']:
        return False
    if filters['max_price'] and product['price'] > filters['max_price']:
        return False

    return True

def get_product_likes(product_id):
    return len(likes[product_id]) if product_id in likes else 0
