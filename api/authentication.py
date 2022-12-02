from flask_mysqldb import MySQL
from flask import Blueprint,request, Response, jsonify
from utils import (
    validate_user_input,
    generate_salt,
    generate_hash,
    db_write,
    validate_user,
    token_required
)
import MySQLdb.cursors
import re

auth_blueprint = Blueprint("auth_blueprint",__name__)

@auth_blueprint.route("/signup",methods=['POST'])
def signup():
    _username = request.json["username"]
    _fullname = request.json["fullname"]
    _user_type = request.json["type"]
    _user_password = request.json["password"]
    #_user_confirm_password = request.form["confirm_password"]

    if validate_user_input("authentication", username= _username, fullname = _fullname, type=_user_type, password=_user_password):
        password_salt = generate_salt()
        password_hash = generate_hash(_user_password, password_salt)
        # return jsonify({"username":_username}), 201
        if db_write(
            """INSERT INTO user (full_name, username, user_type, password_salt, password_hash) VALUES (%s, %s, %s, %s, %s)""",
            (_fullname, _username, _user_type, password_salt, password_hash),):
            
            session_info = validate_user(_username,_user_password);
            if session_info:
                return jsonify({"success":True,"session_info":session_info}),201
            else:
                return Response(status=409)
        else:
            return Response(status=409) 
    else:
        return Response("Username already exists!", status=400)
    

@auth_blueprint.route('/signin', methods=["POST"])
def signIn():
    username = request.json["username"]
    password = request.json["password"]

    session_info = validate_user(username, password)

    if session_info:
        return jsonify({"success":True,"session_info":session_info})
        #return jsonify({"success":True,"jwt_token": user_token,"username":username})
    else:
        return Response(status=401)
    
@auth_blueprint.route('/home',methods=["GET"])
@token_required
def homePage(user):
     return jsonify({
        "message": "successfully retrieved user profile",
        "data": user
    })