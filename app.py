from flask import Flask, request, jsonify,send_file,Response,send_from_directory,render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS
import boto3
from flask_cors import CORS,cross_origin
from flask_mail import Mail,Message


app= Flask(__name__)
# from file import *
CORS(app)
db=SQLAlchemy(app)
ma=Marshmallow(app)
upload_folder="./uploads"
CORS(app)
s3=boto3.client('s3')
basedir=os.path.abspath(os.path.dirname(__file__))
app.config.from_object('config.Development')
mail=Mail(app)
key='secret'
app.config['ALLOWED_DATE']=[]
from routes import *

if __name__ =="__main__":
    app.run(debug=True)
    




