from configparser import ConfigParser
import os

def read_configuration(section_name):
    config_file_path = 'config.ini'
    config_parser = ConfigParser()
    os.chdir('/home/alan/python-projects/weather-info-repo/WeatherInfo')
    if not config_parser.read(config_file_path):
        raise ValueError('Cannot find the configuration file '
            f'{os.path.join(os.getcwd(), config_file_path)}.')
    if config_parser.has_section(section_name):
        config_params = config_parser.items(section_name)
        dictionary = {}
        for key, value in config_params:
            dictionary[key] = value
        return dictionary
    else:
        raise ValueError(f'There is no section "{section_name}" in configuration file'
            f'{os.path.join(os.getcwd(), config_file_path)}.')
    return None
