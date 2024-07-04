import os
from datetime import timedelta
import asyncio
import psycopg2
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("PASSWORD_SQL")
token = os.getenv("TOKEN")

figi_list = ["BBG004731032", "BBG004731354", "BBG004730ZJ9", "BBG004730RP0", "BBG004S681W1", "BBG004730N88", "BBG00475KKY8", "BBG004S68473", "BBG0047315D0", "BBG004S68614"]  # Добавьте здесь ваши FIGI

def get_figi_id(figi_number):
    try:
        conn = psycopg2.connect(
            dbname="financial_db",
            user="postgres",
            password=password,
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

async def fetch_data(figi):
    data = []
    figi_id = get_figi_id(figi)
    if figi_id is None:
        print(f"figi_id not found for {figi}")
        return data
    
    async with AsyncClient(token) as client:
        async for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(minutes=1),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            data.append([
                candle.time,
                candle.open.units + candle.open.nano / 1e9,
                candle.high.units + candle.high.nano / 1e9,
                candle.low.units + candle.low.nano / 1e9,
                candle.close.units + candle.close.nano / 1e9,
                candle.volume,
                figi_id
            ])
    print(data)
    return data

def check_and_insert_data_to_db(data):
    try:
        conn = psycopg2.connect(
            dbname="financial_db",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        for record in data:
            check_query = """
            SELECT 1 FROM candles
            WHERE time_of_candle = %s AND open_price = %s AND high_price = %s AND low_price = %s
            AND close_price = %s AND volume = %s AND figi_id = %s;
            """
            cur.execute(check_query, record)
            exists = cur.fetchone()
            
            if not exists:
                insert_query = """
                INSERT INTO candles (time_of_candle, open_price, high_price, low_price, close_price, volume, figi_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cur.execute(insert_query, record)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error inserting data: {e}")

async def stream_data():
    while True:
        tasks = [fetch_data(figi) for figi in figi_list]
        results = await asyncio.gather(*tasks)
        
        for data in results:
            if data:
                check_and_insert_data_to_db(data)
                
        await asyncio.sleep(60)

async def main():
    await stream_data()

if __name__ == "__main__":
    asyncio.run(main())
