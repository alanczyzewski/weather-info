#!/usr/bin/python3

from model.user import User
from data_access_layer import DataAccessLayer

name = input('name: ')
email = input('email: ')
if not email:
    email = None
phone_number = input('phone number: ')
if not phone_number:
    phone_number = None
city = input('city: ')

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_number = 0
print('\nPick days: ')
for i, day in enumerate(days):
    pick = input(f'{day} (y/n): ').lower()
    days_number += 2**i if pick == 'y' or pick == 'yes' else 0

hour = input('\nhour (0-23): ')
try:
    if int(hour) < 0 or int(hour) > 23:
        raise ValueError
except:
    hour = "7"
 
dal = DataAccessLayer()
if dal.save_user(User(name, days_number, hour, city, phone_number, email)):
    print(f"The user '{name}' has been added to the database")
else:
    print(f"ERROR - Something went wrong")
