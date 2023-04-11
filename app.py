from flask import Flask, render_template, url_for, redirect, request, jsonify, session
import pymysql
from Class import *

db = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='myphone',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


app=Flask(__name__)
app.secret_key = 'my_secret_key'

user = User(db)


#print(user.register("Fabien Brou", "(225)0153148864", "fabienbrou"))

@app.errorhandler(404)
def page_not_found(error):
    # Renvoyer une page de template personnalisée
    return render_template('errors/page_not_found.html'), 404

@app.route('/',  methods=['POST','GET'])
def home():
    print(session)
    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    error = []
    if request.method == 'POST':
        pass
    return render_template('register.html')

@app.route('/confirm', methods=['POST','GET'])
def confirm():
    error = []
    if request.method == 'POST':
        pass
    return render_template('confirm.html')

@app.route('/login', methods=['POST','GET'])
def login():
    error = []
    if request.method == 'POST':
        posted = request.form
    
        result = user.login(posted['phone'], posted['password'])
        if result['success']:
            session['AAMI_ID'] = result['data']['id']
            return redirect(url_for('dashboard'))
        print(result)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    return render_template('customers/index.html')

@app.route('/parameters', methods=['POST','GET'])
def parameters():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    error = []
    if request.method == 'POST':
        pass
    return render_template('customers/parameters.html')

@app.route('/account')
def account():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    return render_template('customers/account.html')

@app.route('/contacts')
def contacts():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    return render_template('customers/contacts.html')

@app.route('/newcontact', methods=['GET', 'POST'])
def addcontact():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    error = []
    if request.method == 'POST':
        pass
    return render_template('customers/addcontact.html')

@app.route('/calls')
def calls():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    return render_template('customers/calls.html')

@app.route('/logout')
def logout():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    session.pop('AAMI_ID', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()  