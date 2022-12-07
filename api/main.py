from flask import Flask, request, render_template
from flask_mysqldb import MySQL
from authentication import auth_blueprint
from assessorController import assesseor_blueprint
from studentController import student_blueprint
from evaluationController import evaluation_blueprint
from flask_ngrok import run_with_ngrok
from flask_cors import CORS, cross_origin

app = Flask(__name__,template_folder='./templates',static_folder='./static')
#run_with_ngrok(app)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'aes_db'
app.config['SECRET_KEY'] = 'JWT_SECRET_KEY'


db = MySQL(app)

app.register_blueprint(auth_blueprint, url_prefix="/api/auth")
app.register_blueprint(assesseor_blueprint, url_prefix="/api/assessor")
app.register_blueprint(student_blueprint, url_prefix="/api/student")
app.register_blueprint(evaluation_blueprint, url_prefix="/api/evaluation")

@app.route('/')
def start():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
    start()
    