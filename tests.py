import os
import unittest
from app import app
import json
from flask_migrate import migrate, upgrade
from models.models import Product, User, Like, db as models_db
from populate import populatedb

def setUpModule():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.config['JWT_SECRET_KEY'] = 'TESTING'

    with app.app_context():
        models_db.create_all()
        populatedb()

def tearDownModule():
    with app.app_context():
        models_db.drop_all()

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_login_success(self):
        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="user1@finland.fi", password="test1FI")),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_login_email_error(self):
        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="invaliduser@finland.fi", password="wrong")),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_passwd_error(self):
        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="user1@finland.fi", password="wrong")),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_feed_unauthenticated(self):
        response = self.app.get('/products/')
        self.assertEqual(response.status_code, 401)

    def test_get_product_unauthenticated(self):
        response = self.app.get('/products/1')
        self.assertEqual(response.status_code, 401)

    def test_like_product_unauthenticated(self):
        response = self.app.post('/products/3/like')
        self.assertEqual(response.status_code, 401)


class TestEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="user1@finland.fi", password="test1FI")),
            content_type='application/json'
        )
        self.access_token = json.loads(response.data)['access_token']

    def tearDown(self):
        pass

    def test_feed(self):
        response = self.app.get(
            '/products/',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 200)
        feed = json.loads(response.data)
        self.assertEqual(len(feed), 15)
        # First element sorted by default by id
        self.assertEqual(feed[0]['description'], 'Leather jacket')

    def test_get_product(self):
        response = self.app.get(
            '/products/13',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 200)
        product = json.loads(response.data)
        self.assertEqual(product['description'], 'Basketball shirt')
        # Testing the price is converted to the right currency
        self.assertAlmostEqual(product['price'], 279.95 / 7.4713, 0)
        self.assertEqual(product['likes'], 0)

    def test_get_product_404(self):
        response = self.app.get(
            '/products/37',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 404)

    def test_like_product(self):
        response = self.app.post(
            '/products/13/like',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 200)
        product = json.loads(response.data)
        self.assertEqual(product['likes'], 1)

    def test_like_product_404(self):
        response = self.app.post(
            '/products/37/like',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 404)

    def test_like_own_product_error(self):
        response = self.app.post(
            '/products/1/like',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 400)

    def test_sorted_feed_by_price(self):
        response = self.app.get(
            '/products/?sort=price&order=DESC',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 200)
        feed = json.loads(response.data)
        self.assertEqual(len(feed), 15)
        self.assertEqual(feed[0]['description'], 'Longchamp handbag')
        self.assertEqual(feed[14]['description'], 'Tank top')

    def test_feed_with_filters(self):
        response = self.app.get(
            '/products/?min_price=10&max_price=30&country=FI',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 200)
        feed = json.loads(response.data)
        self.assertEqual(len(feed), 4)
        items = [product['description'] for product in feed]
        self.assertIn('Star wars t-shirt', items)
        self.assertIn('VANS Sweatshirt', items)
        self.assertIn('High-heel shoes', items)
        self.assertIn('Leather jacket', items)

class TestLikes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        # User 1 logs in and likes stuff
        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="user1@finland.fi", password="test1FI")),
            content_type='application/json'
        )
        token1 = json.loads(response.data)['access_token']
        self.app.post(
            '/products/13/like',
            headers={"Authorization": "Bearer " + token1}
        )
        self.app.post(
            '/products/3/like',
            headers={"Authorization": "Bearer " + token1}
        )
        self.app.post(
            '/products/17/like',
            headers={"Authorization": "Bearer " + token1}
        )

        # User 2 logs in and likes stuff
        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="user2@finland.fi", password="test2FI")),
            content_type='application/json'
        )
        token2 = json.loads(response.data)['access_token']
        self.app.post(
            '/products/13/like',
            headers={"Authorization": "Bearer " + token2}
        )
        self.app.post(
            '/products/17/like',
            headers={"Authorization": "Bearer " + token2}
        )

        # User 3 logs in and likes stuff
        response = self.app.post(
            '/login/',
            data=json.dumps(dict(email="user3@finland.fi", password="test3FI")),
            content_type='application/json'
        )
        token3 = json.loads(response.data)['access_token']
        self.app.post(
            '/products/17/like',
            headers={"Authorization": "Bearer " + token3}
        )

        # We'll use user1 for the test
        self.access_token = token1

    def tearDown(self):
        pass

    def test_sorted_feed_by_likes(self):
        response = self.app.get(
            '/products/?sort=likes&order=DESC',
            headers={"Authorization": "Bearer " + self.access_token}
        )
        self.assertEqual(response.status_code, 200)
        feed = json.loads(response.data)
        self.assertEqual(len(feed), 15)
        self.assertEqual(feed[0]['id'], 17)
        self.assertEqual(feed[0]['likes'], 3)

        self.assertEqual(feed[1]['id'], 13)
        self.assertEqual(feed[1]['likes'], 2)

        self.assertEqual(feed[2]['id'], 3)
        self.assertEqual(feed[2]['likes'], 1)



if __name__ == "__main__":
    unittest.main()
