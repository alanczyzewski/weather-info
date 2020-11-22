from model.language import Language

class User():
    def __init__(self, name:str, days_week:int, time:str, city:str, 
            language:Language, phone_number:str=None, email:str=None, 
            active:bool=True):
        self.name = name
        self.days_week = days_week
        self.time = time
        self.city = city
        self.language = language 
        self.phone_number = phone_number 
        self.email = email
        self.active = active