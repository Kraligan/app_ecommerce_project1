import jwt
from flask import request, jsonify
from model import User
from functools import wraps
import random
import string
from model import Product

JWT_SECRET = "d3fb12750c2eff92120742e1b334479e"

def decode_token(token):
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms="HS256"
        )
    except Exception:
        print("Jeton JWT invalide.")
        return
    
def require_authentication(f):
    @wraps(f)
    def wrapper(**kwargs):
        token = request.headers.get("Authorization", "0")
        if not decode_token(token):
            return jsonify({"error": "Jeton d'acces invalide."}), 401
        return f(**kwargs)
    return wrapper

def check_admin(f):
    @wraps(f)
    def wrapper(**kwargs):
        token = request.headers.get("Authorization", "0")
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"error": "Utilisateur non authentifié"}), 401
        
        if not user.is_admin:
            return jsonify({"error": "Cet utilisateur n'est pas admin"}), 403 
        print("User est bien un admin")
        return f(**kwargs)
    return wrapper

def is_admin():
    token = request.headers.get("Authorization", "0")
    user = User.query.filter_by(token=token).first()
    return user.is_admin if user else False

'''
def generate_random_string(length=5):
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(characters, k=length))
'''

def check_stock(product:Product, quantity):
    return product.stock > quantity