import json
import os
import re

from datetime import datetime

from database.btree import BTree

class Database:
    def __init__(self, name: str, t: int=2, columns: list[str]=None, timestamp: bool=False):
        self.btree: BTree = BTree(t)
        self.filename: str = name + "_keys.json"
        self.columns: list = columns
        self.timestamp: bool = timestamp
        self.dbname: str = name + "_values.txt"
        self.data: dict[int, int] = self._load_data()
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
            
    def insert(self, key: int, value: dict):
        key = str(key)
        
        if not self.columns:
            self.columns = list(value.keys())
        else:
            for k in self.columns:
                assert k in value.keys()
        
        if key in self.data:
            position = self.data[key]
            with open(self.dbname, 'r+') as f:
                f.seek(position)
                f.write("#DELETED#")
        
        with open(self.dbname, 'a') as f:
            position = f.tell()
            j = {key: value}
            if self.timestamp:
                j['timestamp'] = datetime.now().isoformat()
            record = json.dumps(j) + '\n'
            f.write(record)
        
        if key not in self.data:
            self.btree.insert(key)
        self.data[key] = position
        self._save_data()
        
    def search(self, key: int):
        key = str(key)
        if self.btree.search(key):
            position = self.data[key]
            with open(self.dbname, 'r') as f:
                f.seek(position)
                record = json.loads(f.readline().strip())
                return record
        return "Not found"
    
    def get_row(self, key: int):
        key = str(key)
        if self.btree.search(key):
            position = self.data[key]
            with open(self.dbname, 'r') as f:
                f.seek(position)
                return json.loads(f.readline().strip())
        else: print("Not found", key)
    
    def get(self, value: str='*', where: str=None, sortby: str=None, desc: bool=False, top: int=None):
        l = self.btree.traverse()
        if top is not None:
            if desc:
                l = l[:top]
            else: 
                l = l[len(l)-top:]
        tree = []
        if value: value = value.strip()
        if where: where = where.strip()
        for i in l:
            j = self.get_row(i)
            if where is None:
                if value == '*':
                    tree.append(j)
                else:
                    values = re.split(r',\s*', value)
                    tree.append({key: j[key] for key in values if key in j})
            else:
                w = [re.split(r'\s*=\s*', a) for a in re.split(r',\s*', where)]
                add = True
                for key in w:
                    if j[key[0]] != key[1]:
                        add = False
                        break
                if add:
                    if value == '*':
                        tree.append(j)
                    else:
                        values = re.split(r',\s*', value)
                        tree.append({key: j[key] for key in values if key in j})
        
        if sortby is not None:
            tree.sort(key=lambda x: x[sortby], reverse=desc)
        
        return tree
    
    def post(self, value: dict): 
        key = self.btree.max() + 1
        key = str(key)

        if not self.columns:
            self.columns = list(value.keys())
        else:
            for k in self.columns:
                assert k in value.keys()
        
        with open(self.dbname, 'a') as f:
            position = f.tell()
            j = {key: value}
            if self.timestamp:
                j['timestamp'] = datetime.now().isoformat()
            record = json.dumps(j) + '\n'
            f.write(record)
        self.btree.insert(key)
        self.data[key] = position
        self._save_data()
                
    def update(self, key: int, value: dict):
        key = str(key)
        
        if not self.columns:
            self.columns = list(value.keys())
        else:
            for k in self.columns:
                assert k in value.keys()
                
        if self.btree.search(key):
            position = self.data[key]
            with open(self.dbname, 'r+') as f:
                f.seek(position)
                f.write("#DELETED#")
        with open(self.dbname, 'a') as f:
            position = f.tell()
            j = {key: value}
            if self.timestamp:
                j['timestamp'] = datetime.now().isoformat()
            record = json.dumps(j) + '\n'
            f.write(record)
        self.data[key] = position
        self._save_data()
    
    def delete(self, key: int):
        key = str(key)
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
