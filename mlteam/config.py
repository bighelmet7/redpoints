import os

class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False
    TESTING = False
    REDIS_HOST  = ''
    REDIS_PORT  = 6379
    REDIS_DB    = 0
    MAX_WORKERS_CONCURRENCY = 2


class ProductionConfig(Config): pass


class DevelopmentConfig(Config):
    DEBUG = True
    REDIS_HOST = 'localhost'
    MAX_WORKERS_CONCURRENCY = 6


class TestingConfig(Config):
    TESTING = True
    REDIS_HOST = 'localhost'
    MAX_WORKERS_CONCURRENCY = 4
