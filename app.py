"""A simple Hello World! app in Flask."""
import os
import uuid
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

#TODO move from pickledb to something we can query
import pickledb
import minio

mc = minio.Minio(
    "play.min.io",
    access_key=os.environ.get('MINIO_ACCESS_KEY'),
    secret_key=os.environ.get('MINIO_SECRET_KEY'),
)

db = pickledb.load('metadata.db', False)

USERNAME = os.environ.get('MYAPP_USERNAME')
PASSWORD = os.environ.get('MYAPP_PASSWORD')


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
    """
    Authenticates a user with the provided credentials and returns an access token.

    :return: A JSON object containing the access token.
    :rtype: flask.Response
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != USERNAME or password != PASSWORD:
        return jsonify({'message': 'Bad username or password'}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    A protected endpoint. The user must provide a valid access token in the Authorization header.
    
    :return: A JSON object containing a message.
    :rtype: flask.Response
    """
    current_user = get_jwt_identity()    
    return jsonify({'message': 'Access granted', 'user': current_user})

@app.route('/create_object', methods=['POST'])
@jwt_required()
def create_object():
    """
    Create a new object in the bucket.
    
    :return: A JSON object containing a message.
    :rtype: flask.Response
    """
    object_name = str(uuid.uuid4())
    current_user = get_jwt_identity()
    bucket_name = request.json.get('bucket_name', None)
    object_data = request.json.get('object_data', None)
    if mc.bucket_exists(bucket_name) is False:
        mc.make_bucket(bucket_name)
    upload_url = mc.presigned_put_object(bucket_name, object_name)
    metadata = {
        'user': current_user,
        'bucket': bucket_name,
        'object_name': object_name,
        'metadata': object_data
        }
    db.set(object_name, metadata)
    db.dump()
    response = {
        'message': 'Object metadata created.',
        'user': current_user,
        'metadata': metadata,
        'upload_url': upload_url
        }
    return jsonify(response)

@app.route('/get_object_metadata/<object_name>', methods=['GET'])
def get_object_metadata(object_name):
    """
    Get the metadata for the object.
    
    :return: A JSON object containing a message.
    :rtype: flask.Response
    """
    metadata = db.get(object_name)
    if request.args.get('with_url') is not None:
        metadata['download_url'] = mc.presigned_get_object(metadata['bucket'], metadata['object_name'])
    return jsonify(metadata)

@app.route('/get_objects', methods=['GET'])
def get_objects():
    """
    Get the list of objects in the bucket.
    
    :return: A JSON object containing a message.
    :rtype: flask.Response
    """
    objects = [d for d in db.getall()]
    return jsonify(objects)
