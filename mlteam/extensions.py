from requests import Session
from flask_redis import FlaskRedis

session = Session()
redis_client = FlaskRedis()
