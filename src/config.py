import os
from dotenv import load_dotenv
import redis

load_dotenv()

token = os.getenv("TOKEN")
password = os.getenv("PASSWORD_SQL")

figi_list = [
    "BBG004731032", "BBG004731354", "BBG004730ZJ9", 
    "BBG004730RP0", "BBG004S681W1", "BBG004730N88", 
    "BBG00475KKY8", "BBG004S68473", "BBG0047315D0", 
    "BBG004S68614"
]

# Настройка клиента Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
