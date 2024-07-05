from datetime import timedelta
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
import asyncio
from config import TOKEN, figi_list
from db import get_figi_id, get_previous_candle_data, check_and_insert_data_to_db
from cache import cache_candle_data, get_cached_candle_data

async def fetch_data(figi):
    # Проверка наличия данных в кэше
    cached_data = get_cached_candle_data(figi)
    if cached_data:
        print(f"Using cached data for {figi}")
        return cached_data

    data = []
    figi_id = get_figi_id(figi)
    if figi_id is None:
        print(f"figi_id not found for {figi}")
        return data
    
    async with AsyncClient(TOKEN) as client:
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
    
    if not data:
        previous_data = get_previous_candle_data(figi_id)
        if previous_data:
            current_time = now().replace(second=0, microsecond=0, tzinfo=None)
            previous_data = (current_time,) + previous_data + (figi_id,)
            data.append(previous_data)

    # Кэширование данных
    cache_candle_data(figi, data)
    
    print(data)
    return data

async def stream_data():
    while True:
        tasks = [fetch_data(figi) for figi in figi_list]
        results = await asyncio.gather(*tasks)
        
        for data in results:
            if data:
                check_and_insert_data_to_db(data)
                
        await asyncio.sleep(60)
