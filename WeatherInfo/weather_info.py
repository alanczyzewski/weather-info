#!/usr/bin/python3

import json, requests, sys
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from log_config import logging
import config_access_layer
from data_access_layer import DataAccessLayer
from model.user import User

def get_users():
    hour = datetime.now().hour + 1
    week_day = datetime.now().weekday()
    dal = DataAccessLayer()
    return dal.get_users(week_day=week_day, hour=hour, with_email=True)

def get_cities_users(users:list) -> dict:
    cities_users = {}
    for user in users:
        if user.city not in cities_users:
            cities_users[user.city] = [user]
        else:
            cities_users[user.city].append(user)
    return cities_users

def get_key():
    section_name = "api"
    try:
        return config_access_layer.read_configuration(section_name)["key"]
    except ValueError as e:
        logging.error(f'The attempt to get api-key has failed.\nReason:\t\t{str(e)}')
        sys.exit()

def get_weather(city, api_key) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"
    response = download_forecast(url)
    weather_data = json.loads(response)
    try:
        w = weather_data['list']
        timestamp = w[0]['dt']
        date = datetime.fromtimestamp(timestamp)
        forecast = {'date': date}
        for i in range(8):
            hour_forecast = {
                'cloudiness': w[i]['clouds']['all'],
                'temperature': round(w[i]['main']['temp'] - 273.15, 1), # celsius
                'feels like': round(w[i]['main']['feels_like'] - 273.15, 1),
                'pressure': w[i]['main']['pressure'],
                'humidity': w[i]['main']['humidity'],
                'wind': w[i]['wind']['speed'], # meter/sec
                'description': w[i]['weather'][0]['description'],
                'probability of precipitation': w[i]['pop']
            }
            forecast[i] = hour_forecast
        return forecast
    except KeyError as e:
        logging.error('The attempt to read weather forecast from json format has '
            f'failed.\nReason:\t\tKeyError: {str(e)}')
        sys.exit()

def download_forecast(url) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        logging.error('The attempt to get weather from website has failed.'
            f'\nReason:\t\t{str(e)}')
        sys.exit()

def log_in_email():
    credentials = get_smtp_credentials()
    smtpObj = smtplib.SMTP(host=credentials['smtp-hostname'], 
        port=credentials['smtp-port'])
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(credentials['login'], credentials['password'])
    return smtpObj, credentials['email']
    
def send_email(smtpObj:smtplib.SMTP, email_from:str, forecast:dict, user:User):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = user.email
    msg['Subject'] = "Daily Weather Forecast"
    
    message = prepare_email_message(forecast, user)
    msg.attach(MIMEText(message, 'html'))    
    
    smtpObj.send_message(msg)

def get_smtp_credentials() -> dict:
    section_name = "email"
    try:
        return config_access_layer.read_configuration(section_name)
    except ValueError as e:
        logging.error('The attempt to get email credentials has failed.'
            f'\nReason:\t\t{str(e)}')
        sys.exit()

def prepare_email_message(forecast:dict, user:User) -> str:
    message = """<!DOCTYPE HTML><html lang="en"><head><meta charset="utf-8"/><style>
        body { color: #bf00ff; font-size: 100%; font-family: Georgia; background-color: 
        powderblue; } h3 { color: #e68a00; font-size: 2.5em; } h4 { color: #cc7a00; 
        font-size: 1.5em; } #container { width: 390px; margin-left: auto; margin-right: 
        auto; } #welcome { text-align: center; } #footer { text-align: center; 
        opacity: 0.5; color: black; font-size: 1.5em; padding: 10px; } .main_temperature { 
        font-size: 1.8em; color: #4d2e00; } </style> </head> 
        <body> <div id="container"> <div id="welcome"> <h3>Good morning, """ + user.name + """!</h3> 
        </div> <div> <h4>Here is your daily weather forecast for """ + user.city + """:</h4> 
        </div> """
    for i in range(8):
        message += ''.join(('<div> <div class="main_temperature"> <i> ',
            f"{forecast['date'].strftime('%H:%M')} </i>&emsp;<b> ",
            f"{forecast[i]['temperature']}&#176;C</b>&emsp; ",
            f"{forecast[i]['description']}</div> <div>Probability of precipitation: ",
            f"<b>{forecast[i]['probability of precipitation']}%</b> </div> ",
            f"<div>Feels like: <b>{forecast[i]['feels like']}&#176;C</b> </div> ",
            f"<div>Wind: <b>{forecast[i]['wind']} m/s</b> </div> ",
            f"<div>Cloudiness: <b>{forecast[i]['cloudiness']}%</b> </div> ",
            f"<div>Humidity: <b>{forecast[i]['humidity']}%</b> </div> ",
            f"<div>Pressure: <b>{forecast[i]['pressure']} hPa</b> </div> </div> "))
        forecast['date'] += timedelta(hours=3)
    message += '<div id="footer">Have a nice day!</div> </div> </body> </html> '
    return message

def close_connection_email(smtpObj:smtplib.SMTP):
    smtpObj.quit()


try:
    all_users = get_users()
    if not all_users:
        logging.info('None of the users has been informed about the weather.')
        sys.exit()
    cities_users = get_cities_users(all_users)
    api_key = get_key()
    smtpObj, email_from = log_in_email()

    for city, users in cities_users.items():
        forecast = get_weather(city, api_key)
        for user in users:
            logging.info(f"Attempting to send an email to {user.name} ({user.email}).")
            try:
                send_email(smtpObj, email_from, forecast, user)
                logging.info(f'An email has been sent to {user.name} ({user.email}).')
            except smtplib.SMTPException as e:
                logging.error(f'The attempt to send an email to {user.name} '
                    f'({user.email}) has failed.\nReason:\t\t{str(e)}')    
    close_connection_email(smtpObj)
except Exception as e:
    logging.error(f'An unexpected error has occurred while running.\n{str(e)}')
