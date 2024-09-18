from os import environ


POSTGRES_HOST = environ.get('POSTGRES_HOST')
POSTGRES_PORT = environ.get('POSTGRES_PORT')
POSTGRES_DB = environ.get('POSTGRES_DB')
POSTGRES_USER = environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')

DEBUG = True if environ.get('DEBUG').lower() == 'true' else False

CRYPT_CONTEXT_SCHEMA = environ.get('CRYPT_CONTEXT_SCHEMA')
CREPT_CONTEXT_DEPRECATED = environ.get('CREPT_CONTEXT_DEPRECATED')
