from flask import Flask, request, jsonify
import jwt, datetime, os
from flask_mysqldb import MySQL

auth_server = Flask(__name__)

auth_server.config["MYSQL_HOST"] = "localhost"
auth_server.config["MYSQL_USER"] = 'auth_user'
auth_server.config["MYSQL_PASSWORD"] = 'Siddhu_auth'
auth_server.config["MYSQL_DB"] = 'auth'
auth_server.config["MYSQL_PORT"] =3306

mysql = MySQL(auth_server)

# export MYSQL_HOST='localhost'
# export MYSQL_USER='auth_user'
# export MYSQL_PASSWORD='Siddhu_auth'
# export MYSQL_DB='auth'


def create_jwt(username, jwt_secret, authz):
    return jwt.encode(
        payload={
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": authz
        },
        key=jwt_secret,
        algorithm="HS256"
    )

@auth_server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401
    
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email, password FROM user WHERE email=%s", (auth.username,))
    
    if res == 1:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        if auth.password == password:
            token = create_jwt(auth.username, os.environ.get("JWT_SECRET"), True)
            return jsonify(token=token), 200
        else:
            return "Invalid Credentials", 401
    else:
        return "Invalid Credentials", 401

@auth_server.route("/validate", methods=["POST"])
def validate():
    header = request.headers.get('Authorization')
    
    if not header:
        return "Cannot find the token", 401
    
    try:
        token = header
        decoded = jwt.decode(
            jwt=token,
            key=os.environ.get('JWT_SECRET'),
            algorithms=["HS256"]
        )
    except Exception as e:
        return f"Not authorized: {str(e)}", 403
    
    return jsonify(decoded), 200

if __name__ == "__main__":
    auth_server.run(host="0.0.0.0", port=3000, debug=True)
