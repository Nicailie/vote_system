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
def main(request):
    # Depending on the request method and path, call the respective functiton
    if request.method == 'POST' and request.path == '/voters':
        return register(request)
    elif request.method == 'PUT' and request.path == '/voters':
        return update(request)
    elif request.method == 'GET' and request.path.startswith('/voters'):
        return get_student(request)
    elif request.method == 'DELETE' and request.path == '/voters':
        return delete(request)
    elif request.method == 'POST' and request.path == '/elections':
        return create_election(request)
    elif request.method == 'GET' and  request.path.startswith('/elections'):
        return get_election(request)
    elif request.method == 'DELETE' and request.path == '/elections':
        return delete_election(request)
    else:
        return jsonify("Sorry, invalid request"), 400

def register(request): 
    detail = request.get_json() 
    voters_db = db.collection('voters')
    query = voters_db.where('id', '==', detail['id']).get()
    if len(query) > 0:
        return jsonify("Record is already present"), 409
    voters_db.add(detail)
    return jsonify(detail), 201

def update(request):
    get_id = request.get_json()
    voters_db = db.collection('voters')
    query = voters_db.where('id', '==', get_id['id']).get()
    if len(query) == 0:
        return jsonify(get_id), 404
    for doc in query:
        doc.reference.update(get_id)
    return "The student_id was updated", 200

def get_student(request):
    stud_id = request.args.get('id')
    voters_db = db.collection('voters')
    query = voters_db.where('id', '==', stud_id).get()
    if len(query) == 0:
        return jsonify({'error': "The student is not found"}), 404
    for doc in query:
        return jsonify(doc.to_dict()), 200

def delete(request):
    del_id = request.get_json() 
    voters_db = db.collection('voters')
    query = voters_db.where('id', '==', del_id['id']).get()
    count = 0
    for doc in query:
        doc.reference.delete()
        count += 1
    if count == 0:
        return "Oops! Person not found"
    return "The student was deleted", 200


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