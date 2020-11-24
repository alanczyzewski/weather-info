class User():
    def __init__(self, name:str, days_week:int, time:str, city:str, 
            phone_number:str=None, email:str=None, active:bool=True):
        self.name = name
        self.days_week = days_week
        self.time = time
        self.city = city
        self.phone_number = phone_number 
        self.email = email
        self.active = active
