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
UPLOAD_FOLDER = '\static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# 欄位錯誤的問題可能是html 表單設計順序要改的跟後端一樣

#######待辦事項5/26####
# industy上傳的資料show在他的product，並且解決 photo 還有欄位錯誤問題 (hard) //竟然解決了
# industy index 中可以顯示他想要的七個功能 (easy) //先做這個 //解決
# 將所有industy show在customer的index中 (mid) // 解決
#######待辦事項#########


#######待辦事項5/28#####
# cunsumer 點 submit 後 送到 shopping cart //解決
# shopping cart 點選傳送後 送出訂單 shopping cart 那邊有 list 的問題
# cunsumer 送出的訂單會呈現在 industy 的 order 上
#######待辦事項########

#######待辦事項5/29#####
# 美化indexCustomer
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
        # cur = mysql.connection.cursor()
        # command = "SELECT product.pNo, industy.iNo FROM product inner join industy on product.iNo = industy.iNo order by iName"
        # cur.execute(command)
        # cart = cur.fetchall()
        # mysql.connection.commit()
        # cur.close()
        for i in shoppingCart:
            cur = mysql.connection.cursor()
            command = "INSERT INTO `savefood`.`cart` (`cNo`,`pNo`,`iNo`) VALUES ('{}','{}','{}')"
            cur.execute(command.format(str(cNo), i[1:4], i[5:10]))
            mysql.connection.commit()
            cur.close()
        return redirect(url_for("customerCart"))
    else:
        cur = mysql.connection.cursor()
        cNo = session['cNo']
        command = "SELECT product.pNo, industy.iNo,product.pName, product.price, product.pExpire, product.uploadDate, industy.iName, industy.iAddress, industy.iPhone FROM product inner join industy on product.iNo = industy.iNo order by iName"
        cur.execute(command)
        labels = cur.fetchall()
        mysql.connection.commit()

        return render_template("indexCustomer.html", user=user, consumer=labels)

# 幹 list 問題 要怎麼好好地把字串傳送好


@app.route('/customerCart.html', methods=['GET', 'POST'])
def customerCart():

    if request.method == "POST":
        x = random.randrange(1, 1000)
        shoppingCart = session['shoppingCart']
        shoppingCartList = eval(shoppingCart[0])
        for i in shoppingCartList:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO `savefood`.`transaction` (`cNo`,`transTime`) VALUES(%s,%s)", ((
                    str(session['cNo']),  datetime.date.today())))
            mysql.connection.commit()
            cur.close()
        return redirect(url_for("indexCustome",))
    else:
        shoppingCart = session['shoppingCart']
        return render_template("customerCart.html", shoppingCart=shoppingCart)


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


@ app.route('/indexIndusty.html', methods=['GET'])
def indexIndusty():
    return render_template("indexIndusty.html")


@ app.route('/industyProduct.html', methods=['GET'])
def industyProducty():

    if request.method == "GET":
        iNo = session['iNo']
        cursor = mysql.connection.cursor()
        command = "SELECT * FROM savefood.product where iNo ='%s'"
        cursor.execute(command % iNo)
        mysql.connection.commit()
        result = cursor.fetchall()
        cursor.close()
        return render_template("industyProduct.html", product=result)
    return render_template("indexIndusty.html")


################ UPLOAD的時候欄位錯亂 ################
    # session['name'] = details['name']
    # cur = mysql.connection.cursor()
    # command = "SELECT * FROM industy WHERE iName= '%s'"
    # cur.execute(command % name)
    # mysql.connection.commit()
    # result = cur.fetchall()
    # cur.close()

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
        pimg = details['pimg']
        pNo = random.randrange(1, 1000)
        cur = mysql.connection.cursor()
        x = random.randrange(1, 1000)
        cur.execute(
            "INSERT INTO product(pNo,pName,price,pExpire,pimg,iNo,uploadDate) VALUES (%s,%s, %s, %s, %s, %s, %s)", (x, pName, price, pExpire, pimg, str(result[0][0]), datetime.date.today()))
        mysql.connection.commit()
        cur.close()
        del pNo, pExpire, pName, pimg, price
        return render_template("indexIndusty.html")
    return render_template("industyUpload.html")


@ app.route('/industyOrder.html', methods=['GET'])
def industyOrder():
    return render_template("industyOrder.html")


@ app.route('/industyForum.html', methods=['GET'])
def industyForum():
    return render_template("industyForum.html")


@ app.route('/industyChart.html', methods=['GET'])
def industyChart():
    return render_template("industyChart.html")


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000
    )
