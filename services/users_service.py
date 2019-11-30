import json
from werkzeug.security import safe_str_cmp

with open('resources/users.json') as f:
    users = json.load(f)

def get(id):
    return next(user for user in users if user['id'] == id)

def get_by_email(email):
    return next(user for user in users if user['email'] == email)

def authenticate(payload):
    user = get_by_email(payload['email'])
    if user and safe_str_cmp(user['password'], payload['password']):
        return user
