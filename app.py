from flask import Flask
from flask_restplus import Api, Resource, fields
from exception.restrictions import LikeOwnItemException

import services.product_service as Products
import services.users_service as Users

app = Flask(__name__)
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
        return {
            "status": "Logging in"
        }


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
    def get(self):
        filters = self.filters_parser.parse_args()
        sorting = self.sorting_parser.parse_args()

        return Products.feed(Users.get(1), filters, sorting)

@products.route("/<int:id>")
@products.expect(header_parser)
class Product(Resource):
    def get(self, id):
        try:
            return Products.get(Users.get(1), id)
        except StopIteration:
            return 'Not Found', 404

@products.route("/<int:id>/like")
@products.expect(header_parser)
class Like(Resource):
    def post(self, id):
        try:
            product = Products.get(Users.get(1), id)
            return Products.like(Users.get(1), product)
        except LikeOwnItemException:
            return 'Cannot like own items', 400
        except StopIteration:
            return 'Not Found', 404


if __name__ == '__main__':
    app.run(debug=True)