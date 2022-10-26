from flask import Flask, render_template, redirect, request, url_for, jsonify, make_response
# from flask_pymongo import PyMongo
import pymongo
import jwt
import datetime
from functools import wraps
import bcrypt

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'Flask'


client = pymongo.MongoClient("mongodb+srv://m001-student:m001-mongodb-basics@sandbox.frwq2ks.mongodb.net/?retryWrites=true&w=majority")
db = client.antony_test
c = db.calculator


@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithm=["HS256"])
        except:
            return jsonify({'message' : 'Token is invalid'}), 401

        return f(*args, **kwargs)
    return decorated

@app.route('/calculator')
@token_required
def calculator():
    return render_template('calculator.html')

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'This is only available for people with valid tokens.'})

@app.route('/login')
def login():
    auth = request.authorization
    if auth and auth.password:
        x = c.find_one({'user':auth.username})

        try:
            if x['user'] == auth.username and x['password'] == auth.password:
                token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'], algorithm="HS256")
                myquery = {'user': auth.username}
                newvalues = {"$set": {"token": token}}
                c.update_one(myquery, newvalues)
            return token
            return jsonify({'token': jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])})
        except:
            return make_response('Wrong username and password', 401,{'WWW-Authenticate': 'Basic realm="Login Required"'})
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/register')
def register():
    auth = request.authorization

    if auth and auth.password:
        token = jwt.encode({'user': auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],algorithm="HS256")
        # token = str(token)
        c.insert_one({'user': auth.username, 'password': auth.password, 'token': token})
        return token
        return jsonify({'token' : jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])})
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run(debug=True)