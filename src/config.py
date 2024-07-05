import os
from dotenv import load_dotenv

load_dotenv()

PASSWORD = os.getenv("PASSWORD_SQL")
TOKEN = os.getenv("TOKEN")

figi_list = {
    1: "BBG004731032", 
    2: "BBG004731354", 
    3: "BBG004730ZJ9", 
    4: "BBG004730RP0", 
    5: "BBG004S681W1", 
    6: "BBG004730N88", 
    7: "BBG00475KKY8", 
    8: "BBG004S68473", 
    9: "BBG0047315D0", 
    10: "BBG004S68614"
}
