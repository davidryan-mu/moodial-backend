import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from flask_restplus import Resource, Api, fields
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

app= Flask(__name__)
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

plt.switch_backend('Agg')
app.config.from_pyfile('config.py')
api = Api(app,
            version='1.0',
            title='A RESTful API for traking mood.',
            description='Allows users to manage mood diary entries',
            authorizations=authorizations
            )

mongo = PyMongo(app)
jwt = JWTManager(app)

user_collection = mongo.db.user

user_register_model = api.model('User Register',{
    'username': fields.String(description='New username to register', required=True),
    'email': fields.String(description='Email to register',required=True),
    'password': fields.String(description='Password to register',required=True)
})
user_login_model = api.model('User Login', {
    'username': fields.String(description='Username on database',required=True),
    'password': fields.String(description='Password associated with username',required=True)
})

medication = api.model('Medication', {
    'name': fields.String(description='Name of medication'),
    'dose': fields.String(description='Dose in mg')

})
diet = api.model('Diet', {
    'food': fields.String(description='Food eaten'),
    'amount': fields.String(description='Amount eaten')
})
entry_post = api.model('Entry', {
    'mood': fields.Integer(description='The users mood from 0-7',required=True),
    'sleep': fields.Integer(description='How much sleep in hrs'),
    'iritability': fields.Integer(description='Iritability rating from 0-3'),
    'medication': fields.List(fields.Nested(medication)),
    'diet': fields.List(fields.Nested(diet)),
    'exercise': fields.String(description='Did you exercise?'),
    'notes': fields.String(description='Any additional information to include?')
})

class Entry(Resource):
    @classmethod
    def getNextEntryId(cls):
        sequenceDocument = mongo.db.counters.find_one_and_update(
            {"_id": "entryid"},
            {"$inc": {"sequence_value": 1}},
        )
        return sequenceDocument['sequence_value']

    @jwt_required()
    @api.doc(security=authorizations,
            body=entry_post,
            responses= {
                201: 'Entry added successfully',
                500: 'Failed to insert to database'
            },
            description='Will posted entry to database with given body elements')
    def post(self):
        currentDateTime = datetime.utcnow()
        _id = Entry.getNextEntryId()
        _json = request.json
        _postedBy = get_jwt_identity()
        entry = {'_id': _id,
                '_postedBy': _postedBy,
                'date': str(currentDateTime.strftime("%Y-%m-%d")),
                'time': str(currentDateTime.strftime("%H:%M:%S")),
                'mood': _json['mood'],
                'sleep': _json['sleep'],
                'iritability': _json['iritability'],
                'medication': _json['medication'],
                'diet': _json['diet'],
                'exercise': _json['exercise'],
                'notes': _json['notes']
                }
        try:
            mongo.db.entries.insert_one(entry)
            return {"message": "Entry added successfully"}, 201
        except:
            return {"message": "Failed to insert entry to database"}, 500

    @jwt_required()
    @api.doc(security=authorizations,
            responses = {
                            200: 'OK'
                        },
            description='Will return the last submitted entry from the database for user')
    def get(self):  # Returns the last inserted entry for the logged in user ie highest id
        identity = get_jwt_identity()
        entries = mongo.db.entries.find({"_postedBy": identity}).sort("_id", -1).limit(1)
        response = []
        for entry in entries:
            response.append(entry)
        return response, 200

    @jwt_required()
    @api.doc(security=authorizations, description='Will delete the last posted entry from the database')
    def delete(self):  # deletes the last posted entry
        try:
            identity = get_jwt_identity()
            entry_to_delete = mongo.db.entries.find({"_postedBy": identity}).sort("_id", -1).limit(1)
            response = []
            for entry in entry_to_delete:
                response.append(entry)
            entry_id = response[0]['_id']
            mongo.db.entries.delete_one({"_id": entry_id})
            return {"Message": " Entry Deleted"}, 204
        except:
            return {"Message": "Entry cannot be deleted."}


class EntryPut(Resource):
    @jwt_required()
    @api.doc(description='Updates the entry with specified ID, ID = endpoint',
            params={'id': 'Entry id to update'},
            security=authorizations,
            body=entry_post,
            responses={
                204: 'Entry updated',
                500: 'Failed to update entry',
                401: 'Missing authorization header'
            })
    def put(self, id):
        identity = get_jwt_identity()
        _json = request.json
        _postedBy = get_jwt_identity()
        pre_updateEntry = mongo.db.entries.find({"_id": id})
        date = str(pre_updateEntry[0]['date'])
        time = str(pre_updateEntry[0]['time'])
        
        entry = {'_id': id,
                '_postedBy': identity,
                'date': date,
                'time': time,
                'mood': _json['mood'],
                'sleep': _json['sleep'],
                'iritability': _json['iritability'],
                'medication': _json['medication'],
                'diet': _json['diet'],
                'exercise': _json['exercise'],
                'notes': _json['notes']
                }
        try:
            mongo.db.entries.replace_one({'_id' : id}, entry)
            return {'message' : 'Entry updated'} , 204
        except:
            return {'message': 'Failed to update entry'}, 500

class EntryList(Resource):
    @jwt_required()
    @api.doc(security=authorizations,
            responses={
                500: 'Entries not found',
                200: 'OK'
            },
            description='Will return a list of all entries from the database')
    def get(self):  # returns a list of all entries on the DB which were posted by the specific logged in user.
        identity = get_jwt_identity()
        entries = mongo.db.entries.find({"_postedBy": identity})
        response = []
        for entry in entries:
            response.append(entry)
        try:
            return make_response(jsonify(response), 200)
        except:
            return {'message': 'Cannot find your entires'}, 500


class Register(Resource):
    @classmethod
    def getNextUserId(cls):
        sequenceDocument = mongo.db.counters.find_one_and_update(
            {"_id": "userid"},
            {"$inc": {"sequence_value": 1}},
        )
        return sequenceDocument['sequence_value']

    @classmethod
    def find_by_username(cls, username):
        username_to_check = {"username": username}
        query = user_collection.find_one(username_to_check)
        if query is not None:
            user = query
        else:
            user = None
        return user

    @classmethod
    def find_by_email(cls, email):
        email_to_check = {"email": email}
        query = user_collection.find_one(email_to_check)
        if query is not None:
            user = query
        else:
            user = None
        return user

    @api.doc(body=user_register_model,
            responses={200: 'OK',
                        201: 'User added successfully',
                        400: 'User already exists',
                        404: 'User could not be added/ page not found'},
            description='Allows new users to register')
    def post(self):
        _id = Register.getNextUserId()
        _json = request.json
        _username = _json['username']
        _email = _json['email']
        _password = _json['password']
        hashed_password = generate_password_hash(_password)
        user_json = {"_id": _id,
                    "username": _username,
                    "email": _email,
                    "password": hashed_password
                    }

        if Register.find_by_username(_username):
            return {"message": "A user with that name already exists"}, 400

        if Register.find_by_email(_email):
            return {"message": "A user with that email already exists"}, 400

        try:
            if _username and _email and _password:
                user_collection.insert_one(user_json)
                return {'message': 'User added successfully'}, 201
        except:
            return {"message": "User could not be added"}, 404


class UserLogin(Resource):
    @api.doc(body=user_login_model,
            responses={ 200:'User logged in',
                        401:'Invalid username / password'
                        },
            description='Allows existing users to login and provides JWT for other requests.')
    def post(self):
        details = request.json
        user_collection = mongo.db.user
        user_login = user_collection.find_one({'username': details['username']})

        try:
            if user_login and check_password_hash(user_login['password'], details['password']):
                access_token = create_access_token(identity=details['username'])
                return {"message": "User logged in",
                        "JWT": access_token}, 200
            else:
                return {"message": "Invalid username and/or password."}, 401
        except:
            return {'message': 'Invalid username and/or password'}, 401


class DeleteUser(Resource):
    @api.doc(security=authorizations,
            params={'username': 'A username'},
            responses= {
                204: 'User and entries deleted',
                401: 'You do not have the authorization for this',
                404: 'User does not exist'
            },
            description='Deletes all users data from database')
    @jwt_required()
    def delete(self, username):
        if Register.find_by_username(username):
            if get_jwt_identity() == username:
                user_to_delete = {'username': username}
                user_collection.delete_one(user_to_delete)
                entries_to_delete = {'_postedBy': username}
                mongo.db.entries.delete_many(entries_to_delete)
                return {"message": "User and entries deleted"}, 204
            else:
                return {"message": "You do not have the authorization for this!"}, 401
        else:
            return {"message": "User does not exist"}, 404


class Protected(Resource):  # allows testing of authentication checks

    @jwt_required()
    @api.doc(security=authorizations)
    def get(self):
        current_user = get_jwt_identity()
        return {"You are accessing this as": current_user}, 200

api.add_resource(Protected, '/protected')
api.add_resource(Entry, '/entry')
api.add_resource(EntryPut, '/entry/<int:id>', endpoint='id')
api.add_resource(EntryList, '/entrylist')
api.add_resource(Register, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(DeleteUser, '/deleteuser/<string:username>', endpoint='username')

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def index():
    return 'OK'
