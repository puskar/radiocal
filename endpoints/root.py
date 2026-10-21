from flask import Blueprint, jsonify

# Create a blueprint for this endpoint
root_bp = Blueprint('root', __name__)

@root_bp.route('/radiocal/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to the root endpoint!"})
