import psycopg2
from config import PASSWORD

def get_figi_id(figi_number):
    try:
        conn = psycopg2.connect(
            dbname="financial_db",
            user="postgres",
            password=PASSWORD,
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        query = "SELECT figi_id FROM figi_numbers WHERE figi_number = %s;"
        cur.execute(query, (figi_number,))
        figi_id = cur.fetchone()[0]

        cur.close()
        conn.close()
        return figi_id

    except Exception as e:
        print(f"Error fetching figi_id for {figi_number}: {e}")
        return None

def get_previous_candle_data(figi_id):
    try:
        conn = psycopg2.connect(
            dbname="financial_db",
            user="postgres",
            password=PASSWORD,
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        query = """
        SELECT open_price, high_price, low_price, close_price, volume
        FROM candles
        WHERE figi_id = %s
        ORDER BY time_of_candle DESC
        LIMIT 1;
        """
        cur.execute(query, (figi_id,))
        previous_data = cur.fetchone()

        cur.close()
        conn.close()
        return previous_data

    except Exception as e:
        print(f"Error fetching previous candle data for figi_id {figi_id}: {e}")
        return None

def check_and_insert_data_to_db(data):
    try:
        conn = psycopg2.connect(
            dbname="financial_db",
            user="postgres",
            password=PASSWORD,
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        for record in data:
            insert_query = """
            INSERT INTO candles (time_of_candle, open_price, high_price, low_price, close_price, volume, figi_id)
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1
                FROM candles
                WHERE time_of_candle = %s AND figi_id = %s
            );
            """
            cur.execute(insert_query, tuple(record) + (record[0], record[6]))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error inserting data: {e}")
