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
        date = datetime.fromtimestamp(timestamp).replace(second=0, microsecond=0)
        forecast = {'date': date}
        for i in range(8):
            hour_forecast = {
                'cloudiness': w[i]['clouds']['all'],
                'temperature': round(w[i]['main']['temp'] - 273.15, 1), # celsius
                'feels like': round(w[i]['main']['feels_like'] - 273.15, 1),
                'pressure': w[i]['main']['pressure'],
                'humidity': w[i]['main']['humidity'],
                'wind': w[i]['wind']['speed'], # meter/sec
                'description': w[i]['weather'][0]['description']
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

def send_email(forecast:dict, user:User):
    credentials = get_smtp_credentials()
    smtpObj = smtplib.SMTP(host=credentials['smtp-hostname'], 
        port=credentials['smtp-port'])
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(credentials['login'], credentials['password'])
    
    msg = MIMEMultipart()
    msg['From'] = credentials['email']
    msg['To'] = user.email
    msg['Subject'] = "Daily Weather Forecast"
    
    message = prepare_email_message(forecast, user)
    msg.attach(MIMEText(message, 'html'))    
    
    smtpObj.send_message(msg)
    smtpObj.quit()

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
        body { color: #bf00ff; font-size: 20px; font-family: Georgia; background-color: 
        powderblue; } h3 { color: #e68a00; font-size: 30px; } h4 { color: #cc7a00; 
        font-size:21px; } #container { width: 390px; margin-left: auto; margin-right: 
        auto; } #welcome { text-align: center; } #footer { text-align: center; 
        opacity: 0.5; color: black; font-size: 22px; padding: 10px; } .main_temperature { 
        font-size: 24px; color: #4d2e00; } </style> </head> 
        <body> <div id="container"> <div id="welcome"> <h3>Good morning, """ + user.name + """!</h3> 
        </div> <div> <h4>Here is your daily weather forecast for """ + user.city + """:</h4> 
        </div> """
    for i in range(8):
        message += ''.join(('<div> <div class="main_temperature"> <i> ',
            f"{forecast['date'].strftime('%H:%M')} </i>&emsp;<b> ",
            f"{forecast[i]['temperature']}&#176;C</b>&emsp; ",
            f"{forecast[i]['description']}</div> ",
            f"<div>feels like: <b>{forecast[i]['feels like']}&#176;C</b></div>",
            f"<div>wind: <b>{forecast[i]['wind']} m/s</b></div>",
            f"<div>cloudiness: <b>{forecast[i]['cloudiness']}%</b></div>",
            f"<div>humidity: <b>{forecast[i]['humidity']}%</b></div>",
            f"<div>pressure: <b>{forecast[i]['pressure']} hPa</b></div> </div>"))
        forecast['date'] += timedelta(hours=3)
    message += ' <div id="footer">Have a nice day!</div> </div> </body> </html>'
    return message


try:
    all_users = get_users()
    if not all_users:
        logging.info('None of the users has been informed about the weather.')
        sys.exit()
    cities_users = get_cities_users(all_users)
    api_key = get_key()

    for city, users in cities_users.items():
        forecast = get_weather(city, api_key)
        for user in users:
            logging.info(f"Attempting to send an email to {user.name} ({user.email}).")
            try:
                send_email(forecast, user)
                logging.info(f'An email has been sent to {user.name} ({user.email}).')
            except smtplib.SMTPException as e:
                logging.error(f'The attempt to send an email to {user.name} '
                    f'({user.email}) has failed.\nReason:\t\t{str(e)}')
except Exception as e:
    logging.error(f'An unexpected error has occurred while running.\n{str(e)}')
