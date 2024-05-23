from flask import (
    Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
)

from flask_sqlalchemy import SQLAlchemy #importing every extension necessary
#from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import join
import json
import os
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['STATIC_FOLDER'] = 'static'
db = SQLAlchemy(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/otp')
def otp():
    return render_template('otp.html')

@app.route('/otp_sent')
def otp_sent():
    return render_template('otp_sent.html')



if __name__== '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


