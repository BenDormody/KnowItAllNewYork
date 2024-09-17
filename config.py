import os


class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    TIMEZONE = 'EST'
    PORT = os.getenv('PORT')
    DEVELOPMENT_ENV = os.getenv('DEVELOPMENT_ENV')


config = Config()
