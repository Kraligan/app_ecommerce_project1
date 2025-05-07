# API de Gestion de Commandes

Cette application Flask permet de gérer des utilisateurs, des produits, et des commandes dans site e-commerce. Elle utilise SQLAlchemy pour l'ORM.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Deplacer les fichier source dans l'environement virtuel

## Lancement

```bash
python app.py
```
Dans un autre terminal: 
```bash
python test.py
```

## Routes principales (documentation complete de l'API dans swagger.yaml)

- `POST /api/auth/register` : Inscription d'un nouvel utilisateur.
- `POST /api/auth/login` : Connexion et génération de token JWT.
- `GET /api/produits` : Liste tous les produits
- `GET /api/produits/{carac}/{carac_value}` : Récupérer un produit spécifique selon une caracteristique (categorie, id, nom...)
- `POST /api/produits` : Ajouter un produit (admin uniquement)
- `PUT /api/produits/<id>` : Modifier un produit (admin uniquement)
- `DELETE /api/produits/<id>` : Supprimer un produit (admin uniquement)
- `POST /api/commandes` : Créer une commande
- `GET /api/commandes` : Lister les commandes (Admin voit tout, client voit ses commandes)
- `GET /api/commandes/{id}` : Recuperer une commande specifique
- `PATCH /api/commandes/{id}` : Modifier le statut d'une commande (admin uniquement)
- `GET /api/commandes/<id>/lignes` : Voir les lignes d'une commande

## Authentification

Les routes protégées nécessitent un **token** dans l'en-tête HTTP :

```
Authorization: <token>
```

## Modèles

Voir `model.py` pour la structure complète des tables SQLAlchemy.

## Tests

Des exemples de tests sont disponibles dans `test.py`.
