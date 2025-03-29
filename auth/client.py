import bcrypt
import jwt
import os
from dotenv import load_dotenv
import copy
import datetime

from user_db import AuthDatabase

load_dotenv()

class Client:
    def __init__(self):
        self.db = AuthDatabase()
    
    def signup(self, email, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        if self.db.search(email) == "Not found":
            timestamp = datetime.datetime.now(datetime.UTC()).isoformat()
            data = { "timestamp": timestamp }
            self.db.post(email, hashed, data)
            data['email'] = email
            expiration = datetime.datetime.now(datetime.UTC()) + datetime.timedelta(minutes=60)
            data['exp'] = expiration
            return { "data": jwt.encode(data, os.getenv("JWT_SECRET_KEY"), algorithm="HS256") }
        else:
            return {"error": "User already exists"}
    
    def login(self, email, password):
        if self.db.search(email) != "Not found":
            p = self.db.get_password(email)
            success = bcrypt.checkpw(password.encode(), p.encode())
            if success:
                returned = self.db.get_data(email)
                returned["email"] = email
                timestamp = datetime.datetime.now(datetime.UTC()).isoformat
                returned["timestamp"] = timestamp
                expiration = datetime.datetime.now(datetime.UTC()) + datetime.timedelta(minutes=60)
                returned["exp"] = expiration
                return { "data": jwt.encode(returned, os.getenv("JWT_SECRET_KEY"), algorithm="HS256") }
            else: 
                return { "error": "Incorrect password" }
        else: 
            return {"error": "User not found"}
        
    def get_data(self, token):
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            return { "success": payload[payload["email"]] }
        except jwt.ExpiredSignatureError:
            return { "error": "Token has expired" }
        except jwt.InvalidTokenError:
            return { "error": "Invalid token" }
        
    def update_data(self, token, new):
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            payload['data'] = new
            payload['timestamp'] = datetime.datetime.now(datetime.UTC()).isoformat()
            payload['exp'] =  datetime.datetime.now(datetime.UTC()) + datetime.timedelta(minutes=60)
            self.db.update(payload['email'], payload)
            return { "success": jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256") }
        except jwt.ExpiredSignatureError:
            return { "error": "Token has expired" }
        except jwt.InvalidTokenError:
            return { "error": "Invalid token" }
        
    def logout(self, token):
        try: 
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            payload['timestamp'] = datetime.datetime.now(datetime.UTC()).isoformat()
            self.db.update(payload['email'], payload)
            return { "success": payload['exp'] }
        except jwt.ExpiredSignatureError:
            return { "error": "Token has expired" }
        except jwt.InvalidTokenError:
            return { "error": "Invalid token" }  
        