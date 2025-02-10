from flask import Flask
from models import db
from flask_cors import CORS, cross_origin

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "*"}}) 

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'


db.init_app(app)


with app.app_context():
    
    db.create_all()


from auth_routes import auth_bp
app.register_blueprint(auth_bp)

from favorites_routes import favorite_bp
app.register_blueprint(favorite_bp)

if __name__ == "__main__":
    app.run(debug=True)
