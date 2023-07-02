import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import json

class Firebase:
    def __init__(self):
        self.database_url = "https://testcalendar-391408-default-rtdb.firebaseio.com/"
        cred_obj = firebase_admin.credentials.Certificate('database/firebase_cred.json')
        db_app = firebase_admin.initialize_app(cred_obj, {'databaseURL':self.database_url})
        self.db_reference = db
        self.set_ref("/")
    
    def set_ref(self, str):
        self.ref = self.db_reference.reference(str)
    
    def push_json(self, file_contents=None, json_file=None):     
        self.set_ref("/Events/")
        
        if (json_file):
            with open(json_file, "r") as f:
                file_contents = json.load(f)
        
        for key,value in file_contents.items():
            self.ref.push().set(value)
    