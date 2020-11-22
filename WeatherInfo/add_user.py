#!/usr/bin/python3

from model.language import Language
from model.user import User
from data_access_layer import DataAccessLayer

name = input('name: ')
email = input('email: ')
phone_number = input('phone number: ')
if not phone_number:
    phone_number = None
city = input('city: ')

print('\nLanguages: ')
for i, language in enumerate(Language):
    print(i, language.name, sep='. ')
language_nr = input('\nnumber of the language: ')
language = Language(int(language_nr))

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_number = 0
print('\nPick days: ')
for i, day in enumerate(days):
    pick = input(f'{day} (y/n): ').lower()
    days_number += 2**i if pick == 'y' or pick == 'yes' else 0

hour = input('\nhour (0-24): ')

dal = DataAccessLayer()
if dal.save_user(User(name, days_number, hour, city, language, phone_number, email)):
    print(f"The user '{name}' has been added to the database")
else:
    print(f"ERROR - Something went wrong")