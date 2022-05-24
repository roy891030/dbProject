from cgitb import reset
from email.message import EmailMessage
from logging.handlers import RotatingFileHandler
import re
from flask_wtf import FlaskForm
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask import Flask, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask import Flask, session
app = Flask(__name__)
app.config['SECRET_KEY'] = "mis"
app.debug = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'roy891030891030'
app.config['MYSQL_DB'] = 'savefood'
mysql = MySQL(app)

# create a model


# class customer(db.Model):
#     cNo = db.Column(db.Integer, primary_key=True)
#     cName = db.Column(db.String(45), nullable=True)
#     passqord = db.Column(db.Integer, nullable=True)
#     accountNum = db.Column(db.String(20), nullable=True)
#     email = db.Column(db.String(45))
#     violation = db.Column(db.Integer)

#     def __repr__(self):
#         return "<Name %r>" % self.name

# 根目錄


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/index.html', methods=['GET'])
def index_2():
    return render_template("index.html")


# 顧客
@app.route('/customer_login.html', methods=['GET', 'POST'])
def customer_login():
    if request.method == "POST":
        details = request.form
        name = str(details['name'])
        session['name'] = details['name']
        cur = mysql.connection.cursor()
        command = "SELECT * FROM cunsumer WHERE cName= '%s'"
        cur.execute(command % name)
        mysql.connection.commit()
        result = cur.fetchall()
        cur.close()
        if len(result) > 0:
            del result
            return render_template("indexCustomer.html")
        else:
            del result
            return render_template("customer_register.html")

    return render_template("customer_login.html")


@app.route('/customer_register.html', methods=['POST', 'GET'])
def customer_register():
    if request.method == "POST":
        details = request.form
        name = details['name']
        session['name'] = details['name']
        accountNum = details['accountNum']
        password = details['password']
        email = details['email']
        print(email)
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO cunsumer(cName,password,accountNum,email) VALUES (%s, %s, %s, %s)", (name, password, accountNum, email))
        mysql.connection.commit()
        cur.close()
        del name, accountNum, password, email
        return render_template("index.html")
    return render_template("customer_register.html")


@app.route('/indexCustomer.html', methods=['GET'])
def indexCustome():
    return render_template("indexCustomer.html")


# 廠商
@app.route('/industy_login.html', methods=['GET'])
def industy_login():
    return render_template("industy_login.html")


@app.route('/industy_register.html', methods=['GET'])
def industy_register():
    return render_template("industy_register.html")


if __name__ == '__main__':
    app.run()
