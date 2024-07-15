import psycopg2
import os

PASSWORD = os.getenv("PASSWORD_SQL")

def get_db_connection():
    conn = psycopg2.connect(
        dbname="financial_db",
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432"
    )
    return conn
