from datetime import timedelta, datetime
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
from config import TOKEN, figi_list
import json
import asyncio
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def store_candle_data(figi_number, figi, data):
    for item in data:
        key = f"candle_data:{figi_number}_{item['time'].isoformat()}"
        item['time'] = item['time'].isoformat()  
        redis_client.set(key, json.dumps(item)) 
        print(f"Stored data for {figi_number}: {json.dumps(item)}")

async def fetch_data(figi_number, figi):
    data = []
    
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(minutes=1),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            data.append({
                "time": candle.time,
                "open": candle.open.units + candle.open.nano / 1e9,
                "high": candle.high.units + candle.high.nano / 1e9,
                "low": candle.low.units + candle.low.nano / 1e9,
                "close": candle.close.units + candle.close.nano / 1e9,
                "volume": candle.volume,
                "figi_id": figi_number,
            })
    
    if not data:
        print(f"No new data for {figi}")
    else:
        store_candle_data(figi_number, figi, data)
    
    print(data)
    return data

async def stream_data():
    while True:
        tasks = [fetch_data(figi_number, figi) for figi_number, figi in figi_list.items()]
        await asyncio.gather(*tasks)
        await asyncio.sleep(60)

# Запуск основной функции
if __name__ == "__main__":
    asyncio.run(stream_data())
