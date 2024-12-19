from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import random

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Constants
N = 23  # Example small prime for simplicity
g = 5   # Generator
ephemeral_store = {}  # Temporary storage for ephemeral 'b' values

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(128), nullable=False)
    verifier = db.Column(db.String(512), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    salt = data.get("salt")
    verifier = data.get("verifier")

    if not username or not salt or not verifier:
        return jsonify({"message": "Username, salt, and verifier are required"}), 400

    try:
        verifier = int(verifier)  # Convert verifier to integer
    except ValueError:
        return jsonify({"message": "Invalid verifier value"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    new_user = User(username=username, salt=salt, verifier=str(verifier))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login/initiate", methods=["POST"])
def login_initiate():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"message": "Username is required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    b = random.randint(1, N - 1)  # Generate private ephemeral value
    B = pow(g, b, N)  # Public value sent to client

    # Save b temporarily for verification
    ephemeral_store[username] = {"b": b}

    app.logger.info(f"Initiate: Username={username}, b={b}, B={B}, Salt={user.salt}")
    return jsonify({"salt": user.salt, "B": B}), 200


@app.route("/login/verify", methods=["POST"])
def login_verify():
    data = request.get_json()
    username = data.get("username")
    A = int(data.get("A"))
    # Log received values
    app.logger.info(f"Verify: Username={username}, A={A}")
    
    if not username or not A:
        return jsonify({"message": "Invalid parameters"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Retrieve private ephemeral value 'b' for the user
    b = ephemeral_store.pop(username, {}).get("b")  # Remove b after use
    if not b:
        return jsonify({"message": "Session expired or invalid"}), 400

    verifier = int(user.verifier)
    B = pow(g, b, N)

    # Calculate scrambling parameter u = H(A | B)
    u = int(hashlib.sha256(f"{A}:{B}".encode()).hexdigest(), 16) % N

    # Calculate shared secret S
    S_server = pow(A * pow(verifier, u, N), b, N)
    K_server = hashlib.sha256(f"{S_server}".encode()).hexdigest()

    app.logger.info(f"Verify: Username={username}, A={A}, B={B}, u={u}, S_server={S_server}, K_server={K_server}")

    return jsonify({"message": "Login successful", "K_server": K_server}), 200

if __name__ == "__main__":
    app.run(debug=True)
