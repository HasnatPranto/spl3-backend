from flask import Flask, request, render_template
from flask_mysqldb import MySQL
from authentication import auth_blueprint

app = Flask(__name__,template_folder='./templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'aes_db'
app.config['SECRET_KEY'] = 'JWT_SECRET_KEY'
db = MySQL(app)

app.register_blueprint(auth_blueprint, url_prefix="/api/auth")

if __name__ == "__main__":
    app.run(debug=True)