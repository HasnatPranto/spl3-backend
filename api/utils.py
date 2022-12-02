from settings import JWT_SECRET_KEY
from flask_mysqldb import MySQLdb
from hashlib import pbkdf2_hmac
from functools import wraps
from flask import request, abort

import os
import jwt

def db_read(query, params=None):
    from main import db
    cursor = db.connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    entries = cursor.fetchall()
    cursor.close()

    content = []

    for entry in entries:
        content.append(entry)

    return content


def db_write(query, params):
    from main import db
    cursor = db.connection.cursor()
    try:
        cursor.execute(query, params)
        db.connection.commit()
        cursor.close()

        return True

    except MySQLdb._exceptions.IntegrityError:
        cursor.close()
        return False


def generate_salt():
    salt = os.urandom(16)
    return salt.hex()


def generate_hash(plain_password, password_salt):
    password_hash = pbkdf2_hmac(
        "sha256",
        b"%b" % bytes(plain_password, "utf-8"),
        b"%b" % bytes(password_salt, "utf-8"),
        10000,
    )
    return password_hash.hex()


def generate_jwt_token(content):
    token = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")

    return token


def validate_user_input(input_type, **kwargs):
    if input_type == "authentication":
        user = db_read("""SELECT * FROM user WHERE username = %s""", (kwargs["username"],))
        if len(user)==1:
            return False
        else:
            return True


def validate_user(username, password):
    current_user = db_read("""SELECT * FROM user WHERE username = %s""", (username,))

    if len(current_user) == 1:
        saved_password_hash = current_user[0][5]
        saved_password_salt = current_user[0][4]
        password_hash = generate_hash(password, saved_password_salt)

        if password_hash == saved_password_hash:
            user_id = current_user[0][2]
            jwt_token = generate_jwt_token({"id": user_id})
            session_info = ({
                "jwt_token":jwt_token,
                "fullname": current_user[0][1],
                "username":current_user[0][2],
                "type":current_user[0][3]
                })
            return session_info
            #return jwt_token
        else:
            return False

    else:
        return False

#id 0 hash 5 salt 4
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            print(request.headers["Authorization"])
            token = request.headers["Authorization"].split(" ")
            token = None if len(token)==1 else token[1] 
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            current_user= db_read("""SELECT * FROM user WHERE username = %s""", (data['id'],))
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user[0][1:4], *args, **kwargs)

    return decorated