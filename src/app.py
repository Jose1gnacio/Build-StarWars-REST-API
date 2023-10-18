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


@app.route('/users', methods=['POST'])
def add_user():
    
    data = request.get_json()

    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Se requieren los campos 'email' y 'password'"}), 400

    new_user = User(email=data['email'], password=data['password'], is_active=True)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario agregado exitosamente", "user_id": new_user.id}), 201

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.serialize()), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404


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


from flask import request

@app.route('/favorite/planet', methods=['POST'])
def add_favorite_planet():
        
    user_id = request.json.get("user_id")
    planet_id = request.json.get("planet_id")

    if not user_id or not planet_id:
        return jsonify({"error": "user_id y planet_id son campos requeridos"}), 400

    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)

    if not user or not planet:
        return jsonify({"error": "Usuario o planeta no encontrado"}), 404

    favorite = Favorites(user_id=user_id, planet_id=planet_id)
    favorite.save()

    return jsonify({"message": "Planeta agregado a favoritos correctamente"}), 200


@app.route('/favorite/people', methods=['POST'])
def add_favorite_people():
        
    user_id = request.json.get("user_id")
    people_id = request.json.get("people_id")

    if not user_id or not people_id:
        return jsonify({"error": "user_id y people_id son campos requeridos"}), 400

    user = User.query.get(user_id)
    people = People.query.get(people_id)

    if not user or not people:
        return jsonify({"error": "Usuario o peoplea no encontrado"}), 404

    favorite = Favorites(user_id=user_id, people_id=people_id)
    favorite.save()

    return jsonify({"message": "Persona agregada a favoritos correctamente"}), 200

@app.route('/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    user_favorites = Favorites.query.filter_by(user_id=user_id).all()

    serialized_favorites = [favorite.serialize() for favorite in user_favorites]

    return jsonify(serialized_favorites), 200






















    



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
