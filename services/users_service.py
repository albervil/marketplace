import json

with open('resources/users.json') as f:
    users = json.load(f)

def get(id):
    return next(user for user in users if user['id'] == id)