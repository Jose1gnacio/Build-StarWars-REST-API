"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# CREACION USUARIO
@app.route('/users', methods=['POST'])
def add_user():
    
    data = request.get_json()

    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Se requieren los campos 'email' y 'password'"}), 400

    new_user = User(email=data['email'], password=data['password'], is_active=True)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario agregado exitosamente", "user_id": new_user.id}), 201

#1.- Listar todos los registros de people en la base de datos
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    people_list = []
    for person in people:
        person_data = {
            "id": person.id,
            "name": person.name,   
        }
        people_list.append(person_data)
    return jsonify(people_list)

#2.- Listar la información de una sola people
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"message": "Persona no encontrada"}), 404
    person_data = {
        "id": person.id,
        "name": person.name,             
    }
    return jsonify(person_data)


#3.- Listar los registros de planets en la base de datos
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_list = []
    for planet in planets:
        planet_data = {
            "id": planet.id,
            "name": planet.name,                       
        }
        planets_list.append(planet_data)
    return jsonify(planets_list)

#4.- Listar la información de un solo planet
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "Planeta no encontrado"}), 404
    planet_data = {
        "id": planet.id,
        "name": planet.name,        
    }
    return jsonify(planet_data)

#5.- Listar todos los usuarios del blog
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

#5.1.- Listar usuario especifico
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.serialize()), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

#6.- Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    user_favorites = Favorites.query.filter_by(user_id=user_id).all()

    serialized_favorites = [favorite.serialize() for favorite in user_favorites]

    return jsonify(serialized_favorites), 200

#7.- Añade un nuevo planet favorito al usuario actual
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id es un campo requerido"}), 400

    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)

    if not user or not planet:
        return jsonify({"error": "Usuario o planeta no encontrado"}), 404

    favorite = Favorites(user_id=user_id, planet_id=planet_id)
    favorite.save()

    return jsonify({"message": "Planeta agregado a favoritos correctamente"}), 200


#8.- Añade una nueva people favorita al usuario actual
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id es un campo requerido"}), 400

    people = People.query.get(people_id)

    if not people:
        return jsonify({"error": "Persona no encontrada"}), 404

    favorite = Favorites(user_id=user_id, people_id=people_id)
    favorite.save()

    return jsonify({"message": "Persona agregada a favoritos correctamente"}), 200


#9.- Elimina un planet favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id es un campo requerido"}), 400

    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorito eliminado correctamente"}), 200

#9.1. - Elimina una planet de un usuario especifico de sus favoritos
@app.route('/<int:user_id>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet2(user_id, planet_id):
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorito eliminado correctamente"}), 200

#10.- Elimina una people favorita
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id es un campo requerido"}), 400

    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()

    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorito eliminado correctamente"}), 200

#10.1.- Elimina una people de un usuario especifico de sus favoritos
@app.route('/<int:user_id>/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people2(user_id, people_id):
    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()

    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorito eliminado correctamente"}), 200


#11.- POST, PUT AND DELETE PLANET AND PEOPLE
@app.route('/people', methods=['POST'])
def add_people():

    name = request.json.get("name")
   
    if not name:
        return jsonify({"error": "Todos los campos son requeridos"}), 400
    
    people = People()
    people.name = name       
    people.save()
    return jsonify(people.serialize()), 200

    return jsonify({"succes": "Publicación de libro exitosa"}), 200

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_people(people_id):
    people = People.query.get(people_id)

    if not people:
        return jsonify({"error": "Persona no encontrada"}), 404

    data = request.get_json()

    if "name" in data:
        people.name = data["name"]
    
    people.update()
    
    return jsonify(people.serialize()), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):
    people = People.query.get(people_id)

    if not people:
        return jsonify({"error": "Persona no encontrado"}), 404

    people.delete()
    
    return jsonify({"success": "Persona eliminado con éxito"}), 200
   
@app.route('/planets', methods=['POST'])
def add_planet():

    name = request.json.get("name")
   
    if not name:
        return jsonify({"error": "Todos los campos son requeridos"}), 400
    
    planets = Planets()
    planets.name = name       
    planets.save()
    return jsonify(planets.serialize()), 200

    return jsonify({"succes": "Publicación de libro exitosa"}), 200

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planets.query.get(planet_id)

    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    data = request.get_json()

    if "name" in data:
        planet.name = data["name"]
    
    planet.update()
    
    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)

    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    planet.delete()
    
    return jsonify({"success": "Planeta eliminado con éxito"}), 200
   



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
