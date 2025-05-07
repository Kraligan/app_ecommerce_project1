from flask import Flask, request, jsonify
from model import db, Product, Commande, CommandeLine, User
import jwt
from datetime import datetime, timedelta
from external_func import JWT_SECRET, require_authentication, check_admin, is_admin, check_stock

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///e_com.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de l'extension SQLAlchemy avec notre application
db.init_app(app)

# Création des tables au démarrage de l'application
@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

# Inscription d'un nouvel utilisateur (POST /api/auth/register).
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(data)
        id = data.get('id')
        name = data.get('name')
        age = data.get('age')
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)

        print(f"enregistrement de l'utilisateur {name}")
        # Verification si l'utilisateur existe
        existing_user = User.query.filter_by(email=email).first()
        print("existing user :", existing_user)
        if existing_user:
            return jsonify({"message": "Utilisateur déjà inscrit."}), 409  # 409 = Conflict
    
        new_user = User(id=id, name=name, age=age, email=email, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 200 

    except Exception as e:
        db.session.rollback()
        print("Probleme d'enregirstrement de l'utilisateur ...")
        return jsonify({"Error": str(e)}), 500

# Connexion et génération de token JWT (POST /api/auth/login)
@app.route('/api/auth/login', methods=['POST'])
def login():
    body = request.get_json()
    print(body)
    if body and 'email' in body and 'password' in body:
        print(f"Connexion de {body['email']} en cours ...")
        user = User.query.filter_by(email=body['email']).first()
        print(f"Verification du mdp de {user.name}")
        pwd = user.password
        user_id = user.id
        
        try:
            '''
            # Si l'utilisateur a deja un token non expire, on le reutilise
            print(f"actual token: {user.token}")
            if user.token and user.token.get('exp', '') < datetime.utcnow:
                return jsonify({"token": user.token}), 200
            '''
            # Sinon on genere un nouveau token si le mdp est correct
            if body.get("password", "") == pwd:
                print(f"entered pwd: {body['password']}, real pwd: {pwd}")
                token = jwt.encode(
                    {
                        "exp": datetime.utcnow() + timedelta(hours=1),
                        "user": user.id
                    },
                    JWT_SECRET,
                    algorithm="HS256"
                )
                user.token=token

                # Mise a jour de la base de donne avec le token
                db.session.commit()
                print("Utilisateur connecte")

                return jsonify({"token": token}), 200
            else:
                return jsonify({"error": "Indentifiants incorrects."}), 401
        except Exception:
            return jsonify({"error": "User not found, veuillez vous enregistrer avec /api/auth/register"}), 401
    return jsonify({"error": "Veuillez entrez vos identifiants"}), 401

# Recup liste produit et Afficher le catalogue (GET /api/produits)
@app.route("/api/produits", methods=['GET'], endpoint='catalogue')
@require_authentication
def catalogue():
    # Vérifier si des produits existent dans le catalogue
    if Product.query.count() != 0:
        products = Product.query.all()
        print("Les produits : ", products)
        if is_admin():
            products_dict = [p.to_dict_admin() for p in products]
        else:
            products_dict = [p.to_dict() for p in products]
        print("Product dict ; ", products_dict)
        
        return jsonify({"Catalogue": products_dict}), 200
    else:
        return jsonify({"error": "le catalogue est vide"}), 401

# Récupérer un produit spécifique (GET /api/produits/{carac}/{carac_value})
@app.route(f"/api/produits/<caracteristique>/<carac_value>", endpoint='product_by_carac', methods=['GET'])
@require_authentication
def product_by_carac(caracteristique, carac_value):
    try:
        # Verification de la caracteristique desire:
        if caracteristique not in ['id', 'name', 'category']:
            return jsonify({"error": "Caractéristique invalide"}), 400
        
        attr = getattr(Product, caracteristique)

        print(f"Recherche de l'article avec {caracteristique} = {carac_value} : ")
        # Vérifier si le produit existe
        item = Product.query.filter(attr==carac_value).first()
        if not item:
            return jsonify({"error": "Produit non trouvé"}), 404

        return jsonify(item.to_dict()), 200
    
    except Exception as e:
        return jsonify({"Error": str(e)}), 401

# Créer un nouveau produit (POST /api/produits) - Admin uniquement
@app.route('/api/produits', endpoint='add_produit', methods=['POST'])
@require_authentication
@check_admin
def add_produit():
    try:
        product = request.get_json()
        if product:
            print("Attempt to add product : ", product)
            id = product.get('id', None)
            name = product.get('name', None)
            description = product.get('description', None)
            price = product.get('price', None)
            stock = product.get('stock', None)
            category = product.get('category', None)

        # s'assurer que la requete contient tous les elements pour creer un produit
        if id and name and description and price and stock and category:
            # Verifier si le produit existe deja
            if Product.query.filter_by(id=id).count() != 0:
                return jsonify({"Error": f"Produit deja existant. Si vous souhaitez mettre a jour le produit "\
                                f"{id}, utilisez la route PUT /api/produits/{id})"}), 500
            new_product = Product(id=id, 
                                  name=name, 
                                  description=description, 
                                  price=price, 
                                  stock=stock, 
                                  category=category)
            db.session.add(new_product)
            db.session.commit()
        
        return jsonify({"Message": "Product created", "Product": str(new_product)}), 200
    
    except Exception as e:
        return jsonify({"Error": str(e)}), 401
    
# Modifier un produit existant (PUT /api/produits/{id}) - Admin uniquement
@app.route('/api/produits/<id>', endpoint='modify_produit', methods=['PUT'])
@require_authentication
@check_admin
def modify_produit(id):
    print("Recherche de l'article avec l'id : " , id)
    # Vérifier si le produit existe
    try:
        item = Product.query.filter_by(id=str(id)).first()

        if not item:
            return jsonify({"error": f"Produit avec l'id {id} introuvable."}), 404

        print("Item found : ", item)
        to_update = request.get_json()
        print(f"L'admin veut mettre a jour le produit {id} en changeant {to_update}")
        # Mise à jour des champs si présents dans la requête
        for attr in ['name', 'description', 'price', 'stock', 'category']:
            if attr in to_update:
                setattr(item, attr, to_update[attr])
        db.session.commit()

        item_dict = item.to_dict_admin()

        return jsonify({"Message": "Produit mis a jour", "produit" : item_dict}), 200
    
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

# Supprimer un produit (DELETE /api/produits/{id}) - Admin uniquement
@app.route('/api/produits/<id>', endpoint='delete_produit', methods=['DELETE'])
@require_authentication
@check_admin
def delete_produit(id):
    print("Recherche de l'article avec l'id : " , id)
    # Vérifier si le produit existe
    try:
        item = Product.query.filter_by(id=str(id)).first()

        if not item:
            return jsonify({"error": f"Produit avec l'id {id} introuvable."}), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({"Message": f"Product {id} supprime du catalogue"}), 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    
#    Créer une nouvelle commande (POST /api/commandes)
@app.route('/api/commandes', endpoint='create_commande', methods=['POST'])
@require_authentication
def create_commande():
    try:
        command_info = request.get_json()
        print("Info de la commande : ", command_info)

        adress = command_info.get('adress', "")
        products = command_info.get('products', [])

        if not adress or not products:
            return jsonify({'error': 'Adresse et produits requis'}), 400
        
        token = request.headers.get("Authorization", "0")
        user = User.query.filter_by(token=token).first()

        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401

        print(f"Creation de la commande pour l'utilisateur {user.name}")
        command = Commande(user_id=user.id, adress=adress)
        db.session.add(command)
        db.session.flush() # Pour avoir command.id avant le commit

        # Ajout des articles:
        for product in products:
            product_id = product.get('product_id', '')
            quantity = product.get('quantity', 1)
            print("product id : ", product_id)

            # Vérifier si le produit existe
            product_info = Product.query.filter_by(id=product_id).first()
            print("Produit recherche : ", product_info)
            print("stock du produit : ", product_info.stock)
            if not product_info:
                return jsonify({'error': f'Produit {product_id} non trouvé'}), 404
            
            # Verifier les stocks
            if not check_stock(product_info, quantity):
                return jsonify({'error': f'Pas assez de produit en stocks, quantite restante: {product_info.stock}'}), 404
            
            line = CommandeLine(commande_id= command.id,
                                product_id= product_id,
                                quantity= quantity,
                                prix_unitaire= product_info.price
                                )
            new_quantity = product_info.stock - quantity
            # print("new quantity :", new_quantity)
            setattr(product_info, 'stock', new_quantity)
            db.session.add(line)
            db.session.commit()

        command.status = 'validee'

        db.session.commit()

        return jsonify({'message': 'Commande créée avec succès', 'commande_id': command.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#    Récupérer la liste des commandes (GET /api/commandes) - Admin voit tout, client voit ses commandes
@app.route('/api/commandes', endpoint='list_commande', methods=['GET'])
@require_authentication
def list_commande():
    try:
        token = request.headers.get("Authorization", "0")
        user = User.query.filter_by(token=token).first()

        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401
        
        if is_admin():
            commands = Commande.query.all()
        else:
            commands = Commande.query.filter_by(user_id=user.id).all()

        if not commands:
            return jsonify({'error': "Il n'y a pas de commandes"}), 401
        
        commands_dict = [c.to_dict() for c in commands]
        
        return jsonify({"Commandes": commands_dict}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#    Récupérer une commande spécifique (GET /api/commandes/{id})
@app.route('/api/commandes/<id>', endpoint='get_specific_commande', methods=['GET'])
@require_authentication
def get_specific_commande(id):
    try:
        token = request.headers.get("Authorization", "0")
        user = User.query.filter_by(token=token).first()

        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401
        
        if is_admin():
            command = Commande.query.filter_by(id=id).first()
        else: # Un user peut regarder une commande que si elle lui appartient
            command = Commande.query.filter_by(user_id=user.id, id=id).first()
            
        if not command:
            return jsonify({'error': f"Il n'y a pas de commande avec l'id {id}"}), 401
        
        command_dict = command.to_dict()
        
        return jsonify({"Commande trouve": command_dict}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#    Modifier le statut d'une commande (PATCH /api/commandes/{id}) - Admin uniquement
@app.route('/api/commandes/<id>', endpoint='commande_status', methods=['PATCH'])
@require_authentication
@check_admin
def commande_status(id):
    try:
        STATUS = ['en_attente', 'validee', 'expediee', 'annulee']
        command = Commande.query.filter_by(id=id).first()
        status = request.get_json().get('status', None).lower()

        if not status or status not in STATUS:
            return jsonify({'error': f"Indiquez le statut que vous souhaitez mettre a jour. (A choisir parmis {STATUS})"}), 401
        
        command.status = status
        db.session.commit()
        return jsonify({"Message": "Statut mis a jour", "status": status}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


#    Consulter les lignes d'une commande (GET /api/commandes/{id}/lignes)
@app.route('/api/commandes/<id>/lignes', endpoint='commande_lignes', methods=['GET'])
@require_authentication
def commande_lignes(id):
    try:
        token = request.headers.get("Authorization", "0")
        user = User.query.filter_by(token=token).first()

        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401
        
        if is_admin():
            command = Commande.query.filter_by(id=id).first()
        else: # Un user peut regarder une commande que si elle lui appartient
            command = Commande.query.filter_by(user_id=user.id, id=id).first()

        if not command:
            return jsonify({'error': f"Aucune commande trouvée avec l'id {id}"}), 404
        
        lines = [line.to_dict() for line in command.line]
        
        return jsonify({
            "commande_id": id,
            "lignes": lines
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ajout de quelques produits pour avoir un catalogue de base
@app.before_request
def add_sample_data():
    app.before_request_funcs[None].remove(add_sample_data)
    # Vérifier si des produits existent déjà
    if Product.query.count() == 0:
        products = [
            Product(id='je8zng', name='Smartphone Ultra', description='Smartphone pliable', price=799.99, stock=50, category='Smartphone'),
            Product(id='ab9h2p', name='Casque Bluetooth', description='Audio haute qualité', price=129.99, stock=30, category='Audio'),
            Product(id='cd5j7k', name='Livre Python', description='Apprendre Python en profondeur', price=39.99, stock=100, category='Livre')
        ]
        db.session.add_all(products)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)