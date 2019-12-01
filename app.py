from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from exception.restrictions import LikeOwnItemException

import services.product_service as Products
import services.users_service as Users

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

api = Api(app, version='1.0')

login = api.namespace('login', description="Logging in")
products = api.namespace('products', description='Products API')

login_fields = api.model('Resource', {
    'email': fields.String,
    'password': fields.String,
})
@login.route("/")
@login.expect(login_fields)
class Login(Resource):
    def post(self):
        try:
            user = Users.authenticate(api.payload)

            if user:
                access_token = create_access_token(identity=user['id'])
                return {
                    "access_token": access_token
                }
            else:
                return 'The credentials provided were invalid', 401
        except StopIteration:
            return 'No user with those credentials was found', 401


header_parser = api.parser()
header_parser.add_argument('Authorization', location='headers')

@products.route("/")
@products.expect(header_parser)
class Feed(Resource):
    filters_parser = api.parser()
    filters_parser.add_argument('country', help='Country to filter by')
    filters_parser.add_argument('min_price', help='Minimum price to filter by', type=int)
    filters_parser.add_argument('max_price', help='Maximum price to filter by', type=int)
    
    sorting_parser = api.parser()
    sorting_parser.add_argument('sort', help='Criteria to sort by (price or likes)', choices=('price', 'likes'),)
    sorting_parser.add_argument('order', help='Order to sort by (ASC or DESC)', choices=('ASC', 'DESC'),)

    @products.expect(filters_parser, sorting_parser)
    @jwt_required
    def get(self):
        user_id = get_jwt_identity();
        user = Users.get(user_id)

        filters = self.filters_parser.parse_args()
        sorting = self.sorting_parser.parse_args()

        return Products.feed(user, filters, sorting)

@products.route("/<int:id>")
@products.expect(header_parser)
class Product(Resource):

    @jwt_required
    def get(self, id):
        user_id = get_jwt_identity();
        user = Users.get(user_id)

        try:
            return Products.get(user, id)
        except StopIteration:
            return 'Not Found', 404

@products.route("/<int:id>/like")
@products.expect(header_parser)
class Like(Resource):
    
    @jwt_required
    def post(self, id):
        user_id = get_jwt_identity();
        user = Users.get(user_id)

        try:
            product = Products.get(user, id)
            return Products.like(user, product)
        except LikeOwnItemException:
            return 'Cannot like own items', 400
        except StopIteration:
            return 'Not Found', 404


if __name__ == '__main__':
    app.run(debug=True)
