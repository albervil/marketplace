import json
from app import bcrypt

with open('resources/users.json') as f:
    users = json.load(f)

def get(id):
    from models.models import User

    user = User.query.get(id)
    return user

def authenticate(payload):
    from models.models import User

    user = User.query.filter(User.email == payload['email']).one()

    if user and bcrypt.check_password_hash(user.pw_hash, payload['password']):
        return user
