from configparser import ConfigParser
import os, sys
import mysql.connector

from log_config import logging
import config_access_layer
from model.user import User


class DataAccessLayer:
    __section_name = 'mysql_connection_data'
    def __init__(self):
        try:
            db_conn_dict = config_access_layer.read_configuration(
                DataAccessLayer.__section_name)
            if db_conn_dict:
                self.__connect_to_database(db_conn_dict)
        except (ValueError, mysql.connector.errors.Error) as e:
            logging.error('The attempt to connect with the database has failed.\n'
                f'Reason:\t\t{str(e)}')
            sys.exit()

    def __connect_to_database(self, db_conn_dict):
        logging.info('Attempting to connect with the database.')
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

    def save_user(self, user:User) -> bool:
        try:
            values = (user.name, user.phone_number, user.email, user.active, 
                    user.days_week, user.time, user.city)
            query = "INSERT INTO users \
                    (name, phone_number, email, active, days_week, time, city) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.__insert(query, values)
            logging.info(f"The user '{user.name}' has been added to the database.")
            return True
        except mysql.connector.errors.Error as e:
            logging.error(f"The attempt to save user '{user.name}' to the database "
                f"has failed.\nReason:\t\t{str(e)}")
            return False

    def get_users(self, week_day:int, hour:int, with_email:bool=False, 
            with_phone_number:bool=False) -> list:
        try:
            values = (True, week_day, hour)
            query = "SELECT * FROM users WHERE \
                active = %s \
                AND MOD(FLOOR(days_week / POWER(2,%s)), 2) = 1 \
                AND time = %s"
            if with_email:
                query += " AND email != '' AND email IS NOT NULL"
            if with_phone_number:
                query += " AND phone_number != '' AND phone_number IS NOT NULL"
            users_list = self.__select(query, values)
            logging.info("Fetching users from the database succeeded. "
                f"{len(users_list)} users have been fetched.")
            users = []
            for user in users_list:
                users.append(User(name=user[1], phone_number=user[2], email=user[3],
                active=user[4], days_week=user[5], time=user[6], city=user[7]))
            return users
        except mysql.connector.errors.Error as e:
            logging.error("The attempt to get users from the database has failed.\n"
                f"Reason:\t\t{str(e)}")
            return {}
