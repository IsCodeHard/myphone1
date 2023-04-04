from flask import Flask, render_template, url_for, redirect, request, jsonify
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             database='amidb',
                             cursorclass=pymysql.cursors.DictCursor)


app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST','GET'])
def register():
    error = []
    if request.method == 'POST':
        data = request.form

        if not 'phone' in data or data['phone'] == "" or len(data['phone'].strip()) < 8:
            error.append("phone can't be empty")
            
        if not 'fullname' in data or data['fullname'] == "" or len(data['fullname'].strip()) < 5:
            error.append("fullname can't be empty")
            
        if not 'password' in data or data['password'] == "" or len(data['password'].strip()) < 8:
            error.append("password can't be empty")
            
        if error:
            return jsonify(dict(success=False, msg=error))
        
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE phone=%s"
            cursor.execute(sql, (data['phone'],))
            result = cursor.fetchone()
            
            if not result:
                sql = "INSERT INTO users(fullname,phone,account,password) VALUES (%s,%s)"
                cursor.execute(sql, (data['fullname'],data['phone'],500,data['password']))
                connection.commit()
                return "success"
            else:
                return "user phone already exist"
    return render_template('register.html')

@app.route('/login', methods=['POST','GET'])
def login():
    return render_template('login.html')

@app.route('/profil', methods=['POST','GET'])
def profil():
    return render_template('profil.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/refill', methods=['POST','GET'])
def refill():
    return render_template('refill.html')

@app.route('/call/<phone>', methods=['POST'])
def call(phone):
    return render_template('call.html')

@app.route('/logout', methods=['GET'])
def logout(phone):
    return redirect(url_for('home'))