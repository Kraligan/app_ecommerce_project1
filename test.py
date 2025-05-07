import requests
import json
from model import User

def print_response(response):
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

# Creation d'un client
jean = {'id' : '1234',
    'name' : 'Jean',
    'age' : 40,
    'email' : 'jean@test.fr',
    'password' : 'PwdDeJean'}
print(f"Enregistrement du client : {jean}")
creation_jean = requests.post("http://127.0.0.1:5000/api/auth/register", json=jean)
print_response(creation_jean)

#Creation d'un admin
admin = {'id': '0000',
    'name' : 'Admin',
    'age' : 20,
    'email' : 'admin@test.fr',
    'password' : 'PwdDeAdmin', 
    'is_admin':True}
print(f"Enregistrement de l'admin : {admin}")
creation_admin = requests.post("http://127.0.0.1:5000/api/auth/register", json=admin)
print_response(creation_admin)

# Connexion de l'admin
print("Connexion de l'admin : ")
connexion_admin = requests.post("http://127.0.0.1:5000/api/auth/login", json={'email':'admin@test.fr', 
                                                                              'password':'PwdDeAdmin'})
print_response(connexion_admin)
token_admin = json.loads(connexion_admin.content)["token"]
if connexion_admin.status_code == 200:
    print("Connecte!")
else:
    print("Erreur de connexion, Veuillez ressayer!")

# Admin creer un produit
print("Admin ajoute 50 macbook dans le catalogue : ")
macbook = requests.post('http://127.0.0.1:5000/api/produits', json={'id':'dhwauio', 
                                                                'name':'Macbook air', 
                                                                'description':'Laptop de chez apple', 
                                                                'price':1299.99, 
                                                                'stock':50, 
                                                                'category':'Laptop'}, 
                                                                headers={"Authorization": token_admin})
print_response(macbook)
if macbook.status_code == 200:
    print("Produit ajoute au catalogue")
else:
    print("Produit non ajoute!")

# Connexion du client
print("Connexion de jean : ")
connexion_jean = requests.post("http://127.0.0.1:5000/api/auth/login", json={'email':'jean@test.fr', 
                                                                             'password':'PwdDeJean'})
print_response(connexion_jean)
token_jean = json.loads(connexion_jean.content)["token"]
if connexion_jean.status_code == 200:
    print("Connecte!")
else:
    print("Erreur de connexion, Veuillez ressayer!")

# Afficher le catalogue
print("Catalogue :")
catalogue = requests.get("http://127.0.0.1:5000/api/produits", headers={"Authorization": token_jean})
print_response(catalogue)

# Jean cherche le smartphone je8zng
print("Jean cherche le produit je8zng dans le catalogue: ")
je8zng = requests.get("http://127.0.0.1:5000/api/produits/id/je8zng", headers={"Authorization": token_jean})
print_response(je8zng)

# Jean essaye de creer un produit
print("Jean veut ajouter son macbook dans le catalogue: ")
macbook2 = requests.post('http://127.0.0.1:5000/api/produits', json={'id':'dhwauio2', 
                                                                'name':'Macbook air2', 
                                                                'description':'Laptop de chez apple', 
                                                                'price':1299.99, 
                                                                'stock':10, 
                                                                'category':'Laptop'}, 
                                                                headers={"Authorization": token_jean})
print_response(macbook2)
if macbook2.status_code == 200:
    print("Produit ajoute au catalogue")
else:
    print("Produit non ajoute!")

# Admin veut mettre a jour le produit Macbook
print("Admin veut mettre a jour le produit Macbook")
print("Catalogue admin avant :")
catalogue = requests.get("http://127.0.0.1:5000/api/produits", headers={"Authorization": token_admin})
print_response(catalogue)

macbook_update = requests.put('http://127.0.0.1:5000/api/produits/dhwauio', json={ 
                                                                'price': 1500,
                                                                'stock':10, 
                                                                'category':'Laptop'}, 
                                                                headers={"Authorization": token_admin})
print_response(macbook_update)

print("Catalogue admin apres :")
catalogue = requests.get("http://127.0.0.1:5000/api/produits", headers={"Authorization": token_admin})
print_response(catalogue)

# Admin veut supprimer le livre
print("Admin veut supprimer le livre cd5j7k : ")
del_livre = requests.delete('http://127.0.0.1:5000/api/produits/cd5j7k', headers={"Authorization": token_admin})
print_response(del_livre)
print("Catalogue admin apres suppression :")
catalogue = requests.get("http://127.0.0.1:5000/api/produits", headers={"Authorization": token_admin})
print_response(catalogue)

# Jean passe une commande de 2 macbook et 1 Smartphone
print("Jean passe une commande de 2 macbook et 1 Smartphone: ")
command = requests.post('http://127.0.0.1:5000/api/commandes', json={'adress':'adresse de Jean',
                                                                     'products': [
                                                                         {
                                                                    'product_id': 'dhwauio',
                                                                    'quantity': 2
                                                                },
                                                                {
                                                                    'product_id': 'je8zng',
                                                                    'quantity': 1
                                                                }]
                                                                },
                                                                headers={"Authorization": token_jean})
print_response(command)

# Jean passe une deuxieme commande
print("Deuxieme commande de Jean: 1 smartphone")
command2 = requests.post('http://127.0.0.1:5000/api/commandes', json={'adress':'adresse de Jean',
                                                                     'products': [
                                                                         {
                                                                    'product_id': 'je8zng',
                                                                    'quantity': 1
                                                                }]
                                                                },
                                                                headers={"Authorization": token_jean})
print_response(command2)

print("Catalogue admin apres commande : ")
catalogue = requests.get("http://127.0.0.1:5000/api/produits", headers={"Authorization": token_admin})
print_response(catalogue)

# Jean veut regarder l'historique de ses commandes -> return id, status
historique = requests.get('http://127.0.0.1:5000/api/commandes', headers={"Authorization": token_jean})
print_response(historique)

# L'admin update le status de la premier commande de Jean
update_command1 = requests.patch('http://127.0.0.1:5000/api/commandes/1', json={'status': 'Expediee'}, headers={"Authorization": token_admin})
print_response(update_command1)

# Jean veux regarder le status de sa premier commande -> return id, status
get_command1 = requests.get('http://127.0.0.1:5000/api/commandes/1', headers={"Authorization": token_jean})
print_response(get_command1)

# Jean veut regarder les lignes de sa premiere commande -> return id, lines
lines_command1 = requests.get('http://127.0.0.1:5000/api/commandes/1/lignes', headers={"Authorization": token_jean})
print_response(lines_command1)