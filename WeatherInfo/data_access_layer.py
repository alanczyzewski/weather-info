from configparser import ConfigParser
import os, sys
import mysql.connector
from log_config import logging

from model.user import User
from model.language import Language

class DataAccessLayer:
    __config_file_path = 'database.ini'
    __section_name = 'mysql_connection_data'
    def __init__(self):
        try:
            db_conn_dict = self.__read_configuration()
            if db_conn_dict:
                self.__connect_to_database(db_conn_dict)
        except (ValueError, mysql.connector.errors.ProgrammingError) as e:
            logging.error(f'The attempt to connect with the database has failed.\nReason:\t\t{str(e)}')
            sys.exit()

    def __read_configuration(self):
        config_parser = ConfigParser()
        os.chdir('/home/alan/python-projects/weather-info-repo/WeatherInfo')
        if not config_parser.read(DataAccessLayer.__config_file_path):
            raise ValueError(f'Cannot find the configuration file {os.path.join(os.getcwd(), DataAccessLayer.__config_file_path)}')
        if config_parser.has_section(DataAccessLayer.__section_name):
            config_params = config_parser.items(DataAccessLayer.__section_name)
            db_conn_dict = {}
            for key, value in config_params:
                db_conn_dict[key] = value
            return db_conn_dict
        else:
            raise ValueError(f'There is no section "{DataAccessLayer.__section_name}" in configuration file {os.path.join(os.getcwd(), DataAccessLayer.__config_file_path)}')
        return None

    def __connect_to_database(self, db_conn_dict):
        logging.info('Attempting to connect with the database')
        self.__mydb = mysql.connector.connect(**db_conn_dict)
        self.__cursor = self.__mydb.cursor()
        logging.info('The attempt to connect with the database was successful.')
    
    def __select(self, query, values=None):
        if values is None:
            self.__cursor.execute(query)
        else:
            self.__cursor.execute(query, values)
        return self.__cursor.fetchall()

    def __insert(self, query, values):
        self.__cursor.execute(query, values)
        self.__mydb.commit()
        return self.__cursor.lastrowid

    def __update(self, query, values):
        self.__cursor.execute(query, values)
        self.__mydb.commit()
        return self.__cursor.rowcount

    def save_user(self, user:User):
        try:
            values = (user.name, user.phone_number, user.email, user.active, 
                    user.days_week, user.time, user.city, user.language.value)
            query = "INSERT INTO users \
                    (name, phone_number, email, active, days_week, time, city, language) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            self.__insert(query, values)
            logging.info(f"The user '{user.name}' has been added to the database")
        except mysql.connector.errors.Error as e:
            logging.error(f"The attempt to save user '{user.name}' to the database has failed.\nReason:\t\t{str(e)}")
            return False
        return True