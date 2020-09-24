import os
from datetime import datetime
import logging

os.chdir('/home/alan/python-projects/weather-info-repo/WeatherInfo')
logging.basicConfig(filename=f'logs/{datetime.now().date()}.log', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')