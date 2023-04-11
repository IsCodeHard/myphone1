from flask import Flask, render_template, url_for, redirect, request, jsonify, session
import pymysql
from Class import *
import re

#sendSMS()
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
#send_email("fabienbrou99@gmail.com", "test", "Hello")

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
    errors = []
    
    # phone pattern +2250101010101
    phone_pattern = r"\+\d{1,3}\d{9,10}"
    password_pattern = r"^[A-Za-z0-9]{8,}$"

    
    if request.method == 'POST':
        posted = request.form
        
        fullname = posted.get('fullname',"").strip().lower()
        phone = posted.get('phone',"").strip().lower()
        password = posted.get('password',"")
        
        if len(fullname) < 4 or len(fullname) > 50:
            errors.append("Fullname must be between 4 and 50 characteres")
        
        match = re.match(phone_pattern, phone)
        if not match:
            errors.append("Phone don't respect the pattern (+/countryCode/numberPhone)")
        
        match = re.match(password_pattern, password)
        if not match:
            errors.append("Password must contains at least 8 characteres")
            
        if errors:
            return jsonify(dict(success=False, msg=errors))
        
        return user.register(fullname,phone,password)
        
    return render_template('register.html')

@app.route('/confirm', methods=['POST','GET'])
def confirm():
    error = []
    if request.method == 'POST':
        posted = request.form
        
        result = user.activate(posted['phone'], posted['code'])
        if result['success']:
            return jsonify(dict(success=True, msg="Account activated, you can login now <a href='/login'>here</a>"))
        else :
            return jsonify(dict(success=False, msg="code or phone is wrong"))
    return render_template('confirm.html')

@app.route('/login', methods=['POST','GET'])
def login():
    error = []
    if request.method == 'POST':
        posted = request.form
    
        result = user.login(posted['phone'], posted['password'])
        if result['success']:
            session['AAMI_ID'] = result['data']['public_id']
            return redirect(url_for('dashboard'))
        else :
            return result
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    return render_template('customers/index.html', user=user.select_by_public_id(session.get('AAMI_ID')))

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

    return render_template('customers/contacts.html', contacts=user.get_contact(session.get('AAMI_ID')))

@app.route('/newcontact', methods=['GET', 'POST'])
def addcontact():
    if not user.select_by_public_id(session.get('AAMI_ID')):
            return redirect(url_for('home'))

    error = []
    if request.method == 'POST':
        posted = request.form
        
        return user.addcontact(session.get('AAMI_ID'), posted['fullname'], posted['phone'])
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