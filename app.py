import matplotlib.pyplot as plt
from itertools import starmap
import numpy as np
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
from werkzeug.utils import secure_filename
from wtforms import FileField
import random
import os
import datetime
import json
import numpy as np
UPLOAD_FOLDER = '\static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# 欄位錯誤的問題可能是html 表單設計順序要改的跟後端一樣

#######待辦事項5/30#####

# industy 按下 違反規定、確認皆可以刪除order 一個會將cunsumer violation 加一，一個不會  //hard
# 寫評論
#######待辦事項########

app = Flask(__name__)
app.config['SECRET_KEY'] = "mis"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
# session 中 name 有名字 cNo 有它的代碼
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
            # 這邊寫個session撈資料庫的user id
            cur = mysql.connection.cursor()
            command = "SELECT cNo From cunsumer WHERE cunsumer.cName = '%s'"
            cur.execute(command % name)
            mysql.connection.commit()
            cNo = cur.fetchall()
            cur.close()
            session['cNo'] = int(cNo[0][0])
            cur.close()
            del result
            return redirect(url_for("indexCustome",))

        else:
            del result
            return redirect(url_for("customer_register",))

    return render_template("customer_login.html")


@app.route('/customer_register.html', methods=['POST', 'GET'])
def customer_register():
    if request.method == "POST":
        details = request.form
        name = details['name']
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


@app.route('/indexCustomer.html', methods=['GET', 'POST'])
def indexCustome():
    user = session['name']
    if request.method == "POST":  # 這時後就加進購物車
        cNo = session['cNo']
        shoppingCart = request.form.getlist('shoppingCart')
        session['shoppingCart'] = shoppingCart
        for i in shoppingCart:
            cur = mysql.connection.cursor()
            command = "INSERT INTO `savefood`.`cart` (`cNo`,`pNo`,`iNo`) VALUES ('{}','{}','{}')"
            cur.execute(command.format(str(cNo), i[1:5], i[6:11]))
            mysql.connection.commit()
            cur.close()
        return redirect(url_for("customerCart"))
    else:
        details = request.form
        # industyName = details['industyName']
        # session['industyName'] = industyName
        cur = mysql.connection.cursor()
        cNo = session['cNo']
        command = "SELECT product.pNo, industy.iNo,product.pName, product.price, product.pExpire, product.uploadDate, industy.iName, industy.iAddress, industy.iPhone,product.pimg FROM product inner join industy on product.iNo = industy.iNo order by iName"
        cur.execute(command)
        labels = cur.fetchall()
        mysql.connection.commit()
        return render_template("indexCustomer.html", user=user, consumer=labels)


@app.route('/customerCart.html', methods=['GET', 'POST'])
def customerCart():

    if request.method == "POST":
        # x = random.randrange(1, 1000)
        cNo = session['cNo']
        shoppingCart = session['shoppingCart']
        # shoppingCartList = eval(shoppingCart[0])
        for i in shoppingCart:
            cur = mysql.connection.cursor()
            command = "INSERT INTO `savefood`.`records` (`pNo`,`cNo`,`iNo`) VALUES ('{}','{}','{}')"
            cur.execute(command.format(i[1:5], str(cNo), i[6:11]))
            mysql.connection.commit()
            cur.close()
            # cur = mysql.connection.cursor()
            # command = "DELETE FROM `savefood`.`product` WHERE (`pNo` = {})"
            # cur.execute(command.format(i[1:5]))
            # cur.close()
        user = session['name']
        cur = mysql.connection.cursor()
        cNo = session['cNo']
        command = "SELECT product.pNo, industy.iNo,product.pName, product.price, product.pExpire, product.uploadDate, industy.iName, industy.iAddress, industy.iPhone, product.pimg FROM product inner join industy on product.iNo = industy.iNo order by iName"
        cur.execute(command)
        labels = cur.fetchall()
        mysql.connection.commit()

        cur = mysql.connection.cursor()
        cNo = session['cNo']
        command = "DELETE FROM cart WHERE (cart.cNo = '{}')"
        cur.execute(command.format(cNo))
        mysql.connection.commit()
        return render_template("indexCustomer.html", user=user, consumer=labels)
    else:
        command = "SELECT cunsumer.cName,product.pName,product.price,product.pExpire,product.pimg,industy.iName,industy.iAddress\
        FROM cart\
        INNER JOIN cunsumer ON  cart.cNo= cunsumer.cNo\
        INNER JOIN product ON cart.pNo=product.pNo\
        inner Join industy on cart.iNo=industy.iNo\
        where cunsumer.cNo ={}"
        cNo = session['cNo']
        cur = mysql.connection.cursor()
        cur.execute(command.format(cNo))
        labels = cur.fetchall()
        mysql.connection.commit()
        shoppingCart = session['shoppingCart']
        return render_template("customerCart.html", shoppingCart=labels)


@ app.route('/customerAbout.html', methods=['GET', 'POST'])
def customerAbout():
    user = session['name']
    if request.method == "POST":
        details = request.form
        name = details['name']
        session['name'] = details['name']
        accountNum = details['accountNum']
        password = details['password']
        email = details['email']

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE `savefood`.`cunsumer` SET `cName` = '{0}', `password` = '{1}', `accountNum` = '{2}', `email` = '{3}' WHERE (`cNo` = '{4}');".format(str(name), str(password), str(accountNum), str(email), session['cNo']))
        mysql.connection.commit()
        cur.close()
    #     del name, accountNum, password, email
        return redirect(url_for("indexCustome",))
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cNo = session['cNo']
        command = "SELECT * From cunsumer WHERE cunsumer.cNo = '%s'"
        cur.execute(command % cNo)
        labels = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template("customerAbout.html", user_template=user, consumer=labels)

        # 廠商


@ app.route('/industy_login.html', methods=['GET', 'POST'])
def industy_login():
    if request.method == "POST":
        details = request.form
        name = str(details['name'])
        session['name'] = details['name']
        cur = mysql.connection.cursor()
        command = "SELECT * FROM industy WHERE iName= '%s'"
        cur.execute(command % name)
        mysql.connection.commit()
        result = cur.fetchall()
        cur.close()

        if len(result) > 0:
            del result
            cursor = mysql.connection.cursor()
            command = "SELECT iNo FROM savefood.industy where iName ='%s'"
            cursor.execute(command % name)
            mysql.connection.commit()
            result = cursor.fetchall()
            session['iNo'] = result[0][0]
            cur.close()
            return render_template("indexIndusty.html")
        else:
            del result
            return redirect(url_for("industy_register",))

    return render_template("industy_login.html")


@ app.route('/industy_register.html', methods=['GET', 'POST'])
def industy_register():
    if request.method == "POST":
        details = request.form
        name = details['name']
        session['name'] = details['name']
        address = details['address']
        password = details['password']
        phone = details['phone']
        x = random.randrange(1000, 9999)
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO industy(iNo,iName,iAddress,iPhone,password) VALUES (%s,%s, %s, %s, %s)", (x, name, address, phone, password))
        mysql.connection.commit()
        cur.close()
        del name, address, password, phone
        return render_template("index.html")
    return render_template("industy_register.html")


@ app.route('/customerForum<name>', methods=['GET', 'POST'])
def customerForum(name):
    if request.method == "POST":
        details = request.form
        fName = details['fName']
        cMessage = details['cMessage']
        score = details['score']
        cNo = session['cNo']
        cur = mysql.connection.cursor()
        command = "INSERT INTO `savefood`.`message` (`fName`, `iName`, `cNo`, `cMessage`, `score`) VALUES (%s,%s,%s, %s, %s)"
        cur.execute(command, (str(fName), str(name),
                    str(cNo), str(cMessage), str(score)))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('indexCustome'))
    # industyName = session['industyName']
    else:
        iName = name
        cur = mysql.connection.cursor()
        command = "SELECT fname,cMessage,score \
                from savefood.message \
                where iName = '{}'"
        cur.execute(command.format(name))
        mysql.connection.commit()
        message = cur.fetchall()
        cur.close()
        return render_template("customerForum.html", name=name, message=message)


@ app.route('/indexIndusty.html', methods=['GET'])
def indexIndusty():
    return render_template("indexIndusty.html")


@ app.route('/industyProduct.html', methods=['GET', 'POST'])
def industyProducty():
    if request.method == "POST":

        product = request.form.getlist('product')
        print(product)
        for i in product:
            cur = mysql.connection.cursor()
            command = "DELETE FROM `savefood`.`product` WHERE (`pNo` = '{}')"
            cur.execute(command.format(i[1:5]))
            mysql.connection.commit()
            cur.close()
        return redirect(url_for("industyProducty"))

    else:
        iNo = session['iNo']
        cursor = mysql.connection.cursor()
        command = "SELECT * FROM savefood.product where iNo ='%s'"
        cursor.execute(command % iNo)
        mysql.connection.commit()
        result = cursor.fetchall()
        cursor.close()
        return render_template("industyProduct.html", product=result)


@ app.route('/industyUpload.html', methods=['GET', 'POST'])
def industyUpload():
    if request.method == "POST":
        name = session['name']
        cursor = mysql.connection.cursor()
        command = "SELECT iNo FROM savefood.industy where iName ='%s'"
        cursor.execute(command % name)
        mysql.connection.commit()
        result = cursor.fetchall()
        cursor.close()
        details = request.form
        pName = details['name']
        price = details['price']
        pExpire = details['pExpire']
        file = request.files["pimg"]
        file.save(os.path.join("static", file.filename))
        pimg = str("/static/"+file.filename)
        pNo = random.randrange(1000, 9999)
        cur = mysql.connection.cursor()
        x = random.randrange(1000, 9999)
        cur.execute(
            "INSERT INTO product(pNo,pName,price,pExpire,iNo,uploadDate,pimg) VALUES (%s, %s, %s, %s, %s, %s, %s)", (x, pName, price, pExpire, str(result[0][0]), datetime.date.today(), pimg))
        mysql.connection.commit()
        cur.close()
        del pNo, pExpire, pName, price
        return render_template("indexIndusty.html")
    return render_template("industyUpload.html")


@ app.route('/industyOrder.html', methods=['GET', 'POST'])
def industyOrder():
    if request.method == "POST":
        if request.form['action'] == 'Get':
            product = request.form.getlist('product')
            for i in product:
                cur = mysql.connection.cursor()
                command = "DELETE FROM `savefood`.`product` WHERE (`pNo` = '{}')"
                cur.execute(command.format(i[1:5]))
                mysql.connection.commit()
                cur.close()

                cur = mysql.connection.cursor()
                command = "DELETE FROM `savefood`.`records` WHERE (`pNo` = '{}' and `cNo` = '{}')"
                cur.execute(command.format(str(i[1:5]), str(i[6:10])))
                mysql.connection.commit()
                cur.close()
            return redirect(url_for("industyOrder"))

        if request.form['action'] == 'Violation':
            product = request.form.getlist('product')
            for i in product:
                cur = mysql.connection.cursor()
                command = "DELETE FROM `savefood`.`product` WHERE (`pNo` = '{}')"
                cur.execute(command.format(i[1:5]))
                mysql.connection.commit()
                cur.close()

                cur = mysql.connection.cursor()
                command = "DELETE FROM `savefood`.`records` WHERE (`pNo` = '{}' and `cNo` = '{}')"
                cur.execute(command.format(i[1:5], i[7:11]))
                mysql.connection.commit()
                cur = mysql.connection.cursor()
                command = "UPDATE `savefood`.`cunsumer` SET `violation` = '%s' WHERE (`cNo` = '%s')"
                cur.execute(command % ('1', i[7:11]))
                mysql.connection.commit()
                cur.close()

            return redirect(url_for("industyOrder"))

    else:
        iNo = session['iNo']
        cur = mysql.connection.cursor()
        command = "SELECT product.pNo, cunsumer.cNo,iName,cName,email,violation,pName,price,pimg FROM((records INNER JOIN industy ON records.iNo = industy.iNo)INNER JOIN cunsumer ON records.cNo = cunsumer.cNo)INNER JOIN product ON records.pNo = product.pNo where records.iNo={}"
        cur.execute(command.format(iNo))
        mysql.connection.commit()
        result = cur.fetchall()
        cur.close()
        return render_template("industyOrder.html", result=result)


@ app.route('/industyForum.html', methods=['GET'])
def industyForum():
    name = session['name']
    cur = mysql.connection.cursor()
    command = "SELECT fname,cMessage,score \
        from savefood.message \
        where iName = '{}'"
    cur.execute(command.format(name))
    mysql.connection.commit()
    message = cur.fetchall()
    cur.close()
    return render_template("industyForum.html", message=message)


@ app.route('/industyChart.html', methods=['GET'])
def industyChart():
    name = session['name']
    contain = []
    star = []
    for i in range(0, 6):
        star = calculateStar(name, i)
        contain.append(len(star))
    iNo = session['iNo']
    # results = list(yourUpload(iNo))
    # result = []
    # date = []
    # num = []
    # for j in range(0, len(results[0])+1):
    #     result.append(list(results[j]))
    #     date.append(result[j][0])
    #     num.append(result[j][1])
    return render_template("industyChart.html", contain=contain, )


def calculateStar(name, number):
    cur = mysql.connection.cursor()
    command = "SELECT score \
                FROM savefood.message \
                where iName='{}' and score ={}"
    cur.execute(command.format(name, number))
    mysql.connection.commit()
    result = cur.fetchall()
    cur.close()
    return result


def yourUpload(iNo):
    cur = mysql.connection.cursor()
    command = "SELECT uploadDate  ,count(uploadDate) \
            FROM savefood.product \
            where iNo = '{}' \
            group by iNo,uploadDate \
            order by uploadDate"
    cur.execute(command.format(iNo))
    mysql.connection.commit()
    result = cur.fetchall()
    cur.close()
    return result


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000
    )
