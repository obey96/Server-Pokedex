from flask import Blueprint, request, jsonify
from models import FavoritePokemon, User, db
from flask_cors import CORS, cross_origin
import jwt

favorite_bp = Blueprint('favorites', __name__)
SECRET_KEY = "your_jwt_secret"

def get_current_user(token):
    try:
        token_final= token.split(" ")[1]
        decoded = jwt.decode(token_final, SECRET_KEY, algorithms=["HS256"])
        return User.query.get(decoded["user_id"])
    except Exception as e:
        print(f"error:{e}")

        return None

# Get Favorites
@cross_origin()
@favorite_bp.route('/getFavorites', methods=['GET','OPTIONS'])
def get_favorites():
    if request.method == 'OPTIONS':
        return _handle_preflight()
    token = request.headers.get('Authorization')
    user = get_current_user(token)
    print(token)
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
        #response.headers.add("Access-Control-Allow-Origin", "*")
        # return response

    favorites = [
        {"pokemon_name": fav.pokemon_name, "pokemon_sprite_url": fav.pokemon_sprite_url}
        for fav in user.favorites]
    response = jsonify({"favorites": favorites})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

@favorite_bp.route('/favorites', methods=['POST', 'OPTIONS'])
def add_favorite():
    print("request method: "+request.method)
    if request.method == 'OPTIONS':
        return _handle_preflight()
    
    data = request.get_json()
    pokemon_name = data.get('pokemon_name')
    user_id = data.get('user_id')
    pokemon_sprite_url = data.get('pokemon_sprite_url')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    
    if not pokemon_name:
        return jsonify({"message": "Pokemon name is required"}), 400

    favorite = FavoritePokemon(pokemon_name=pokemon_name, user_id=user_id, pokemon_sprite_url=pokemon_sprite_url)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Pokemon added to favorites!"}), 201

@favorite_bp.route('/favorites/<pokemon_name>', methods=['DELETE', 'OPTIONS'])
def delete_favorite(pokemon_name):
    if request.method == 'OPTIONS':
        return _handle_preflight()
    
    token = request.headers.get('Authorization')
    user = get_current_user(token)
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    # Find the favorite Pokémon entry for the user
    favorite = FavoritePokemon.query.filter_by(user_id=user.id, pokemon_name=pokemon_name).first()
    if not favorite:
        return jsonify({"message": "Favorite Pokémon not found"}), 404

    # Delete the favorite Pokémon entry
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": f"{pokemon_name} removed from favorites!"}), 200


# Helper to handle CORS preflight
def _handle_preflight():
    response = jsonify({"message": "Preflight OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS,DELETE")
    return response
