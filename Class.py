import uuid
import hashlib
import random
import string

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
                    return dict(success=True, msg="Inserted ok!", data=[])
            except Exception as e:
                return dict(success=False, msg=e, data=[])
            finally:
                self.db.close()
        return dict(success=False, msg="Phone already exist", data=[])
            
    def login(self, phone, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = self.select_by_phone(phone)
        if user and user['password'] == hashed_password:
            return dict(success=True, msg="", data=user)
        else:
            return dict(success=False, msg="Invalid credentials!", data=[])
            
    def select_by_phone(self, phone):
        with self.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE phone = %s"
            cursor.execute(sql, (phone,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result['public_id'],
                    'fullname': result['fullname'],
                    'phone': result['phone'],
                    'password': result['password']
                }
            else:
                return False
            
    def select_by_public_id(self, public_id):
        with self.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE public_id = %s"
            cursor.execute(sql, (public_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result['public_id'],
                    'fullname': result['fullname'],
                    'phone': result['phone'],
                    'password': result['password']
                }
            else:
                return False
            
    def activate(self, phone, code):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("UPDATE users SET active = 1 WHERE phone = %s AND code = %s", (phone,code))
                self.db.commit()
            return dict(success=True, msg="Account activate, your can login now", data=[])
        except Exception as e:
            return dict(success=False, msg=e, data=[])
        finally:
            self.db.close()