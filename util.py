class Event:
    def __init__(self, date, time, cmi, agenda):
        self.date = date
        self.time = time
        self.cmi = cmi
        self.agenda = agenda

    def to_string(self):
        print(self.date, self.time, self.cmi, self.agenda)
        
class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id