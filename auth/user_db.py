import json
import os
import re

from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.btree import BTree

class AuthDatabase:
    def __init__(self):
        self.btree: BTree = BTree(2)
        self.filename: str = "user_keys.json"
        self.dbname: str = "users.txt"
        self.data: dict[str, list[str, int]] = self._load_data()
        for i in self.data:
            self.btree.insert(i)
        
    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)
            
    def __len__(self):
        return len(self.btree)
        
    def search(self, key: str):
        if self.btree.search(key):
            position = self.data[key]
            with open(self.dbname, 'r') as f:
                f.seek(position)
                record = json.loads(f.readline().strip())
                return record
        return "Not found"
    
    def get_password(self, email: str):
        password = self.data[email][0]
        return password
        
    def get_data(self, email: str):
        position = self.data[email][1]
        with open(self.dbname, 'r') as f:
            f.seek(position)
            return json.loads(f.readline().strip())

    
    def post(self, email: str, password: str, value: dict): 
        with open(self.dbname, 'a') as f:
            position = f.tell()
            j = {"data": value}
            j['timestamp'] = datetime.now().isoformat()
            record = json.dumps(j) + '\n'
            f.write(record)
        self.btree.insert(email)
        self.data[email] = [password, position]
        self._save_data()
                
    def update(self, email: str, value: dict):
        if self.btree.search(email):
            position = self.data[email]
            with open(self.dbname, 'r+') as f:
                f.seek(position)
                f.write("#DELETED#")
        with open(self.dbname, 'a') as f:
            position = f.tell()
            j = {email: value}
            j['timestamp'] = datetime.now().isoformat()
            record = json.dumps(j) + '\n'
            f.write(record)
        self.data[email] = (self.data[email][0], position)
        self._save_data()
    
    def delete(self, key: str):
        if self.btree.search(key):
            position = self.data[key]
            with open(self.dbname, 'r+') as f:
                f.seek(position)
                f.write("#DELETED#")
            self.btree.delete(key)
            self._save_data()
            return {"key": key}
        else: 
            return "Not found"
