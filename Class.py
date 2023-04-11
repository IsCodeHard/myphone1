import uuid
import hashlib
import random
import string
from flask import jsonify
from sendSMS import sendSMS

def generate_unique_code():
    # generate a random 4-digit number
    unique_digits = random.randint(0, 9999)
    unique_digits_string = str(unique_digits).zfill(4) # zero-pad the number to 4 digits
    
    # generate a random string of uppercase letters
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    
    # combine the digits and letters into a unique code
    unique_code = f"AAMI-{random_letters}-{unique_digits_string}"
    
    return unique_code

class User:
    def __init__(self, db):
        self.db = db
    
    def register(self, fullname, phone, password):
        user = self.select_by_phone(phone)
        if not user:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            public_id = str(uuid.uuid4())
            code=generate_unique_code()
            
            try:
                with self.db.cursor() as cursor:
                    sql = "INSERT INTO users (public_id, fullname, phone, password, code) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (public_id, fullname, phone, hashed_password, code))
                    self.db.commit()
                    sendSMS("AAMI", phone, f"you activation code is {code}")
                    return jsonify(dict(success=True, msg="Inserted ok! Activate your account on here <a href='/confirm'>activate</a>", data=[]))
            except Exception as e:
                return jsonify(dict(success=False, msg=e, data=[]))
            finally:
                self.db.close()
        return jsonify(dict(success=False, msg="Phone already exist", data=[]))
            
    def login(self, phone, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            with self.db.cursor() as cursor:
                sql = "SELECT * FROM users WHERE phone = %s AND password = %s AND active=1"
                cursor.execute(sql, (phone,hashed_password))
                result = cursor.fetchone()
                if result:
                    return dict(success=True, msg="Login", data=result)
                else:
                    return dict(success=False, msg="Invalid credentials", data=[])
        except Exception as e:
            return dict(success=False, msg=e, data=[])
            
    def select_by_phone(self, phone):
        with self.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE phone = %s"
            cursor.execute(sql, (phone,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return False
            
    def select_by_public_id(self, public_id):
        with self.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE public_id = %s"
            cursor.execute(sql, (public_id,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return False
            
    def select_by_id(self, id):
        with self.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return False
            
    def activate(self, phone, code):
        try:
            with self.db.cursor() as cursor:
                sql = "SELECT * FROM users WHERE phone = %s AND code = %s"
                cursor.execute(sql, (phone,code))
                result = cursor.fetchone()
                if result:
                    cursor.execute("UPDATE users SET active = 1 WHERE phone = %s AND code = %s", (phone,code))
                    self.db.commit()
                    return dict(success=True, msg="Account activate, your can login now", data=[])
                return dict(success=False, msg="Account activate, your can login now", data=[])
        except Exception as e:
            return dict(success=False, msg=e, data=[])
        
    def addcontact(self, public_id, fullname, phone):
        user = self.select_by_public_id(public_id)
        if user:
            try:
                with self.db.cursor() as cursor:
                    sql = "INSERT INTO contacts (fullname, phone, user_id) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (fullname, phone, user['id']))
                    self.db.commit()
                    return jsonify(dict(success=True, msg="Contact added!", data=[]))
            except Exception as e:
                return jsonify(dict(success=False, msg=e, data=[]))
        return jsonify(dict(success=False, msg="User doesn't exist", data=[]))
    
    def get_contact(self, public_id):
        user=self.select_by_public_id(public_id)
        if user:
            with self.db.cursor() as cursor:
                sql = "SELECT * FROM contacts WHERE user_id = %s"
                cursor.execute(sql, (user['id'],))
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    return []