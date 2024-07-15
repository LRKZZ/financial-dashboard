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

figi_list = ["BBG004731032", "BBG004731354", "BBG004730ZJ9", "BBG004730RP0", "BBG004S681W1", "BBG004730N88", "BBG00475KKY8", "BBG004S68473", "BBG0047315D0", "BBG004S68614"]

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

def get_previous_candle_data(table_name, figi_id):
    try:
        conn = psycopg2.connect(
            dbname="financial_db",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        query = f"""
        SELECT open_price, high_price, low_price, close_price, volume
        FROM {table_name}
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

async def fetch_data(figi, interval, table_name, candle_interval):
    data = []
    figi_id = get_figi_id(figi)
    if figi_id is None:
        print(f"figi_id not found for {figi}")
        return data
    
    async with AsyncClient(token) as client:
        async for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(minutes=1),
            interval=candle_interval,
        ):
            data.append((
                candle.time,
                candle.open.units + candle.open.nano / 1e9,
                candle.high.units + candle.high.nano / 1e9,
                candle.low.units + candle.low.nano / 1e9,
                candle.close.units + candle.close.nano / 1e9,
                candle.volume,
                figi_id
            ))
    
    if not data:
        previous_data = get_previous_candle_data(table_name, figi_id)
        if previous_data:
            current_time = now().replace(second=0, microsecond=0, tzinfo=None)
            previous_data = (current_time,) + previous_data + (figi_id,)
            data.append(previous_data)

    #print(data)
    return data

def check_and_insert_data_to_db(data, table_name):
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
            insert_query = f"""
            INSERT INTO {table_name} (time_of_candle, open_price, high_price, low_price, close_price, volume, figi_id)
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1
                FROM {table_name}
                WHERE time_of_candle = %s AND figi_id = %s
            );
            """
            cur.execute(insert_query, tuple(record) + (record[0], record[6]))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error inserting data: {e}")

async def stream_1_min_data():
    while True:
        tasks = [fetch_data(figi, 1, "candles", CandleInterval.CANDLE_INTERVAL_1_MIN) for figi in figi_list]
        results = await asyncio.gather(*tasks)
        
        for data in results:
            if data:
                check_and_insert_data_to_db(data, "candles")
                
        await asyncio.sleep(60) # 1 минута

async def stream_5_min_data():
    while True:
        tasks = [fetch_data(figi, 5, "candles_5_min", CandleInterval.CANDLE_INTERVAL_5_MIN) for figi in figi_list]
        results = await asyncio.gather(*tasks)
        
        for data in results:
            if data:
                check_and_insert_data_to_db(data, "candles_5_min")
                
        await asyncio.sleep(300)  # 5 минут

async def stream_10_min_data():
    while True:
        tasks = [fetch_data(figi, 10, "candles_10_min", CandleInterval.CANDLE_INTERVAL_10_MIN) for figi in figi_list]
        results = await asyncio.gather(*tasks)
        
        for data in results:
            if data:
                check_and_insert_data_to_db(data, "candles_10_min")
                
        await asyncio.sleep(600)  # 10 минут

async def stream_60_min_data():
    while True:
        tasks = [fetch_data(figi, 60, "candles_60_min", CandleInterval.CANDLE_INTERVAL_HOUR) for figi in figi_list]
        results = await asyncio.gather(*tasks)
        
        for data in results:
            if data:
                check_and_insert_data_to_db(data, "candles_60_min")
                
        await asyncio.sleep(3700)  # 60 минут

async def main():
    task1 = asyncio.create_task(stream_1_min_data())
    task2 = asyncio.create_task(stream_5_min_data())
    task3 = asyncio.create_task(stream_10_min_data())
    task4 = asyncio.create_task(stream_60_min_data())
    await asyncio.gather(task1, task2, task3, task4)

if __name__ == "__main__":
    asyncio.run(main())
