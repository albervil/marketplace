import json
from app import bcrypt
from src.models import User

def get(id):
    user = User.query.get(id)
    return user

def authenticate(payload):
    user = User.query.filter(User.email == payload['email']).one()

    if user and bcrypt.check_password_hash(user.pw_hash, payload['password']):
        return user
