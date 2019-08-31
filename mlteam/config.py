import os

class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False
    TESTING = False
    REDIS_URL = ""
    MAX_WORKERS_CONCURRENCY = 2


class ProductionConfig(Config): pass


class DevelopmentConfig(Config):
    DEBUG = True
    REDIS_URL = "redis://localhost:6379/0"
    MAX_WORKERS_CONCURRENCY = 6


class TestingConfig(Config):
    TESTING = True
    REDIS_URL = "redis://localhost:6379/0"
    MAX_WORKERS_CONCURRENCY = 4
