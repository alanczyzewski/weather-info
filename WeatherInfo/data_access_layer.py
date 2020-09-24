from configparser import ConfigParser
import os, sys
import mysql.connector
from log_config import logging

class DataAccessLayer:
    __config_file_path = 'database.ini'
    __section_name = 'mysql_connection_data'
    def __init__(self):
        try:
            db_conn_dict = self.__read_configuration()
            if db_conn_dict:
                self.__connect_to_database(db_conn_dict)
        except (ValueError, mysql.connector.errors.ProgrammingError) as e:
            logging.error(f'The attempt to connect to the database has failed.\nReason:\t\t{str(e)}')
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
        logging.info('Attempting to connect to the database')
        self.__mydb = mysql.connector.connect(**db_conn_dict)
        self.__cursor = self.__mydb.cursor()
        logging.info('The attempt to connect to the database was successful.')
    
    def __select(self, query, val=None):
        if val is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, val)
        return self.cursor.fetchall()

    def __insert(self, query, val):
        self.cursor.execute(query, val)
        self.mydb.commit()
        return self.cursor.lastrowid

    def __update(self, query, val):
        self.cursor.execute(query, val)
        self.mydb.commit()
        return self.cursor.rowcount