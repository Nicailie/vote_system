import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import flask
from flask import jsonify, request
import os
import functions_framework

cred = credentials.Certificate('key.json')
new = firebase_admin.initialize_app(cred, name="Vote")
db = firestore.client(app=new)
app = flask.Flask(__name__)

@app.route('/', methods=['POST', 'DELETE', 'PUT', 'GET', 'PATCH'])
def main_try(request):
    # Check if request method is allowed
    if request.method not in ['POST', 'DELETE', 'PUT', 'GET', 'PATCH']:
        return jsonify("Invalid request method"), 400

    # Call the respective function based on the request method and path
    if request.method == 'POST' and request.path == '/voters':
        return register(request)
    elif request.method == 'PUT' and request.path == '/voters':
        return update(request)
    elif request.method == 'GET' and request.path == '/voters':
        return get_voter(request)
    elif request.method == 'DELETE' and request.path == '/voters':
        return delete(request)
    else:
        return jsonify("Invalid request path"), 400


def register(request):
    # Check if request body is valid JSON
    try:
        detail = request.get_json()
    except ValueError:
        return jsonify("Invalid request body"), 400

    # Check if voter with the same ID already exists
    query = voters_db.where('id', '==', detail['id']).get()
    if len(query) > 0:
        return jsonify("Record with the same ID already exists"), 409

    # Add voter to the database
    try:
        voters_db.add(detail)
    except:
        return jsonify("Failed to add record to the database"), 500

    return jsonify(detail), 201


def update(request):
    # Check if request body is valid JSON
    try:
        get_id = request.get_json()
    except ValueError:
        return jsonify("Invalid request body"), 400

    # Check if voter with the given ID exists
    query = voters_db.where('id', '==', get_id['id']).get()
    if len(query) == 0:
        return jsonify("Record not found"), 404

    # Update the voter in the database
    try:
        for doc in query:
            doc.reference.update(get_id)
    except:
        return jsonify("Failed to update record in the database"), 500

    return jsonify(get_id), 200


def get_voter(request):
    # Get the voter ID from query parameter
    stud_id = request.args.get('id')

    # Check if voter with the given ID exists
    query = voters_db.where('id', '==', stud_id).get()
    if len(query) == 0:
        return jsonify("Record not found"), 404

    # Return the voter details
    for doc in query:
        return jsonify(doc.to_dict()), 200


def delete(request):
    # Check if request body is valid JSON
    try:
        del_id = request.get_json()
    except ValueError:
        return jsonify("Invalid request body"), 400

    # Check if voter with the given ID exists
    query = voters_db.where('id', '==', del_id['id']).get()
    count = 0
    for doc in query:
        # Delete the voter from the database
        try:
            doc.reference.delete()
            count += 1
        except:
            return jsonify("Failed to delete record from the database"), 500

    if count == 0:
        return jsonify("Record not found"), 404

    return jsonify(del_id), 200



def create_election(request):
    election = request.get_json()
    election_db = db.collection('elections')  
    query = election_db.where('el_id', '==', election['el_id']).get()
    if len(query) > 0:
        return jsonify("You are duplicating it"), 409
    election_db.add(election)
    return jsonify(election), 201


def get_election(request):
    election_id = request.args.get('el_id')
    election_db = db.collection('elections')
    query = election_db.where('el_id', '==', election_id).get()
    if len(query) == 0:
        return jsonify({'error': "The election was not found"}), 404
    for doc in query:
        return jsonify(doc.to_dict()), 200

def delete_election(request):
    delet_id = request.get_json() 
    election_db = db.collection('elections') 
    query = election_db.where('el_id', '==', delet_id['el_id']).get()
    count = 0
    for doc in query:
        doc.reference.delete()
        count += 1
    if count == 0:
        return jsonify(delet_id), 404
    return "The election is deleted", 200

if __name__ == '__main__':
    app.run()
