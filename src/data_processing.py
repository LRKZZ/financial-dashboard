from datetime import timedelta, datetime
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
import asyncio
from config import TOKEN, figi_list, redis_client
import json

def cache_candle_data(figi, data):
    key = f"candle_data:{figi}"
    for item in data:
        item['time'] = item['time'].isoformat()  # Преобразование datetime в строку
    redis_client.set(key, json.dumps(data), ex=60)  # Кэширование данных на 60 секунд
    print(f"Cached data for {figi}: {json.dumps(data)}")

def get_cached_candle_data(figi):
    key = f"candle_data:{figi}"
    cached_data = redis_client.get(key)
    if cached_data:
        data = json.loads(cached_data)
        for item in data:
            item['time'] = datetime.fromisoformat(item['time'])  # Преобразование строки обратно в datetime
        print(f"Retrieved cached data for {figi}: {data}")
        return data
    print(f"No cached data found for {figi}")
    return None

async def fetch_data(figi):
    # Проверка наличия данных в кэше
    cached_data = get_cached_candle_data(figi)
    if cached_data:
        print(f"Using cached data for {figi}")
        return cached_data

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
            })
    
    if not data:
        # Handle case where no new data is available
        print(f"No new data for {figi}")
    
    # Кэширование данных
    cache_candle_data(figi, data)
    
    print(data)
    return data

async def stream_data():
    while True:
        tasks = [fetch_data(figi) for figi in figi_list]
        await asyncio.gather(*tasks)
        await asyncio.sleep(60)
