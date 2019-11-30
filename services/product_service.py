import json
import services.users_service as Users
from exception.restrictions import LikeOwnItemException
from services.currency_conversion_service import convert_currency_base_eur

likes = {}
with open('resources/products.json') as f:
    products = json.load(f)


def feed(user, filters, sorting):
    feed = [
        extend(product, user) for product in products \
        if (product['user'] != user['id'] \
        and pass_filters(extend(product, user), filters))
    ]
    sort_field = sorting['sort']

    if sorting['sort']:
        desc_sort = sorting['order'] is not None and sorting['order'] == 'DESC' 
        print(sort_field)
        return sorted(feed, key=lambda prod: prod[sort_field], reverse=desc_sort)
    else:
        return feed

def get(user, id):
    product = next(prod for prod in products if prod['id'] == id)
    return extend(product, user)

def like(user, product):
    if user['id'] == product['user']:
        raise LikeOwnItemException()

    if id in likes.keys():
        likes[product['id']].add(user['id'])
    else:
        likes[product['id']] = {user['id']}
    
    product['likes'] = get_product_likes(product['id'])
    return product


def extend(product, buyer):
    seller = Users.get(product['user'])
    product_currency = seller['currency']
    convert_from_eur = (product_currency == 'EUR')

    price = product['price'] if buyer['currency'] == product_currency \
                            else convert_currency_base_eur(
                                product['price'], product_currency, convert_from_eur
                            ) 

    result = product.copy()

    result['country'] = seller['country']
    result['price'] = price 
    result['likes'] = get_product_likes(product['id'])
    return result

def pass_filters(product, filters):
    if filters['country'] and product['country'] != filters['country']:
        return False
    if filters['min_price'] and product['price'] < filters['min_price']:
        return False
    if filters['max_price'] and product['price'] > filters['max_price']:
        return False

    return True

def get_product_likes(product_id):
    return len(likes[product_id]) if product_id in likes else 0
