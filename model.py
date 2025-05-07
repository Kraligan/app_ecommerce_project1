from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialisation de l'extension SQLAlchemy
db = SQLAlchemy()

# Définition des modèles Utilisateurs: Client (User) et Administrateur (Admin)
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(1000), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100), default=None)
    is_admin = db.Column(db.Boolean, default = False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    commande = db.relationship('Commande', backref='user', uselist=False)

    def __repr__(self):
        return f"User: {self.name}, id: {self.id}, admin: {'yes' if self.is_admin else 'no'}"


# Definition des modeles de gestion des produits
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Product {self.name}, price: {self.price}, categorie: {self.category}, disponibilite: {self.disponible()}>'

    def to_dict(self): # Sans stock
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "disponible": self.disponible()
        }
    
    def to_dict_admin(self): # Avec stock
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "stock": self.stock,
            "disponible": self.disponible()
        }
    
    def disponible(self):
        return self.stock > 0

class Commande(db.Model):
    __tablename__ = 'commande'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(10), db.ForeignKey('user.id'), nullable=False)
    adress = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='en_attente')
    
    # Relation avec les éléments de la commande
    line = db.relationship('CommandeLine', backref='commande', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Commande {self.id}, status {self.status}>'
    
    def to_dict(self): 
        return {
            "comande_id": self.id,
            "status": self.status
        }

class CommandeLine(db.Model):
    __tablename__ = 'commande_line'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'), nullable=False)
    product_id = db.Column(db.String(10), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)
    
    # Relation avec le produit
    product = db.relationship('Product', backref='commande_line')
    
    def __repr__(self):
        return f'<CommandeLine {self.id}, Product: {self.product_id}, Qty: {self.quantity}, prix unitaire: {self.prix_unitaire}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "prix_unitaire": self.prix_unitaire
        }