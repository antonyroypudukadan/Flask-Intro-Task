from flask import Flask, render_template, redirect, request, url_for, g, jsonify, make_response
import pymongo
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'Flask'

client = pymongo.MongoClient("mongodb+srv://m001-student:m001-mongodb-basics@sandbox.frwq2ks.mongodb.net/?retryWrites=true&w=majority")
db = client.antony_test
c = db.calculator
b=db.blacklist

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        g.token = token
        f = b.find_one({'btoken': token})
        # try:
        if not f:
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithm=["HS256"])
            except:
                return jsonify({'message': 'Token is invalid'}), 401

            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Token blacklisted'}), 401
        # except:
        #     return jsonify({'message': 'Token blacklisted'}), 401
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
    print(vars(request))
    if auth and auth.password:
        x = c.find_one({'user':auth.username})

        try:
            if x['user'] == auth.username and x['password'] == auth.password:
                token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'], algorithm="HS256")
            return token
        except:
            return make_response('Wrong username and password', 401,{'WWW-Authenticate': 'Basic realm="Login Required"'})
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user = request.form['name']
        password = request.form['password']
        c.insert_one({'user': user, 'password': password})
    return render_template('register.html')

@app.route("/logout/<token>")
def logout(token):
    b.insert_one({'btoken':token})
    return jsonify({'message': 'Logged Out'})


if __name__ == '__main__':
    app.run(debug=True)