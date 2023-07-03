import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import json

class Firebase:
    def __init__(self):
        try:
            self.database_url = "https://testcalendar-391408-default-rtdb.firebaseio.com/"
            cred_obj = firebase_admin.credentials.Certificate('firebase_cred.json')
            db_app = firebase_admin.initialize_app(cred_obj, {'databaseURL':self.database_url})
            self.db_reference = db
            self.set_ref("/")
            
            self.connection = True
        except:
            self.connection = False
    
    def set_ref(self, str):
        self.ref = self.db_reference.reference(str)
    
    def get_or_create_user(self, chat_id):
        if (not self.connection):
            return
        
        self.set_ref("/Users/")
        users = self.ref.get()
                
        if (not users or not chat_id in list(map(lambda s: s["chat_id"], users.values()))):
            user_dict = {"chat_id": chat_id}
            self.ref.push().set(user_dict)
            
    def get_or_create_song(self, song_name):
        if (not self.connection):
            return
        
        self.set_ref("/Songs/")
        songs = self.ref.get()
                
        if (not songs or not song_name in list(map(lambda s: s["song_name"], songs.values()))):
            song_dict = {"song_name": song_name}
            self.ref.push().set(song_dict)
            
    def create_event(self, event_json):
        if (not self.connection):
            return
            
        self.set_ref("/Events/")
        self.ref.push().set(event_json)
    
    def push_json(self, file_contents=None, json_file=None):     
        self.set_ref("/Events/")
        
        if (json_file):
            with open(json_file, "r") as f:
                file_contents = json.load(f)
        
        for key,value in file_contents.items():
            self.ref.push().set(value)
    