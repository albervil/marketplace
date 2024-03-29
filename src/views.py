from app import app
from flask_restplus import Api, Resource, fields

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from src.exception.restrictions import LikeOwnItemException
from sqlalchemy.orm.exc import NoResultFound

import src.services.product_service as Products
import src.services.users_service as Users

api = Api(app, version='1.0')
jwt = JWTManager(app)

# To fix dumb Flask bug that causes Error 500 if endpoints are called without authorization header
jwt._set_error_handler_callbacks(api)

login = api.namespace('login', description="Logging in and obtaining access token")
products = api.namespace('products', description='Products API')

login_fields = api.model('Resource', {
    'email': fields.String(description="The user's email", example="user1@finland.fi"),
    'password': fields.String(description="The user's password", example="test1FI")
})
@login.route("/")
@login.doc(
    responses={200: 'Access token for the user', 401: 'Unauthorized'}
)
@login.expect(login_fields)
class Login(Resource):
    def post(self):
        """
        Sign in and get an authorization token.
        """
        try:
            user = Users.authenticate(api.payload)

            if user:
                access_token = create_access_token(identity=user.id)
                return {
                    "access_token": access_token
                }
            else:
                return 'The credentials provided were invalid', 401
        except NoResultFound:
            return 'No user with those credentials was found', 401


header_parser = api.parser()
header_parser.add_argument('Authorization', help='Bearer \{Token\}', location='headers')

@products.route("/")
@products.doc(
    responses={200: 'The product feed for the user'}
)
class Feed(Resource):
    filters_parser = api.parser()
    filters_parser.add_argument('country', help='Country to filter by')
    filters_parser.add_argument('min_price', help='Minimum price to filter by', type=int)
    filters_parser.add_argument('max_price', help='Maximum price to filter by', type=int)

    sorting_parser = api.parser()
    sorting_parser.add_argument('sort', help='Criteria to sort by (price or likes)', choices=('price', 'likes'),)
    sorting_parser.add_argument('order', help='Order to sort by (ASC or DESC)', choices=('ASC', 'DESC'),)

    @products.expect(header_parser, filters_parser, sorting_parser)
    @jwt_required
    def get(self):
        """
        Shows the product feed for the user.
        """
        user_id = get_jwt_identity()
        user = Users.get(user_id)

        filters = self.filters_parser.parse_args()
        sorting = self.sorting_parser.parse_args()

        return Products.feed(user, filters, sorting)

@products.route("/<int:id>")
@products.doc(
    params={'id': 'Product ID'},
    responses={200: 'The requested product', 404: 'Not Found'}
)
@products.expect(header_parser)
class Product(Resource):

    @jwt_required
    def get(self, id):
        """
        Shows details of an individual product.
        """
        user_id = get_jwt_identity()
        user = Users.get(user_id)

        product = Products.get(user, id)

        if product is not None:
            return Products.get(user, id)
        else:
            return 'Not Found', 404

@products.route("/<int:id>/like")
@products.doc(
    params={'id': 'Product ID'},
    responses={
        200: 'The product with the computed like',
        400: 'Bad Request: Cannot like own items',
        404: 'Not Found'
    }
)
@products.expect(header_parser)
class Like(Resource):

    @jwt_required
    def post(self, id):
        """
        Likes the selected product.
        """
        user_id = get_jwt_identity()
        user = Users.get(user_id)

        try:
            product = Products.like(user, id)

            if product is not None:
                return product
            else:
                return 'Not Found', 404
        except LikeOwnItemException:
            return 'Cannot like own items', 400

