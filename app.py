"""A simple Hello World! app in Flask."""
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity 



app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'VFVR%^E^HGERERW4r3f4e3erv5g4F$#G$##$'
jwt = JWTManager(app)

@app.route("/")
def hello_world():
    """Return a friendly HTTP greeting.

    Returns:
        str: A string containing a friendly greeting message.
    """
    return "<p>Hello, World!</p>"


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != 'test':  # Replace with your own authentication logic
        return jsonify({'message': 'Bad username or password'}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'Access granted'})

