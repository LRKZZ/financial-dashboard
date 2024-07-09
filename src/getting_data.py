import asyncio
import redis
from datetime import datetime, timedelta, timezone
from tinkoff.invest import AsyncClient, CandleInterval
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Подключение к Redis
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

TOKEN = os.getenv("TOKEN")

# Список figi
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

async def save_to_redis(figi_id, candle_data):
    key = f"{figi_id}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
    redis_client.set(key, json.dumps(candle_data))
    print(f"Данные записаны в Redis: {key}")

async def get_last_redis_data(figi_id):
    keys = redis_client.keys(f"{figi_id}_*")
    if keys:
        key = f"{figi_id}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        last_key = sorted(keys)[-1]
        last_value = redis_client.get(last_key)

        value_dict = json.loads(last_value.decode("utf-8"))[0]
        dt = datetime.fromisoformat(value_dict["time"])
        dt_plus_one_minute = dt + timedelta(minutes=1)
        value_dict["time"] = dt_plus_one_minute.isoformat()

        updated_value = json.dumps([value_dict])
        redis_client.set(key, updated_value)

        return json.loads(redis_client.get(last_key))
    
    return None

async def fetch_data_for_figi(client, figi_id, figi):
    from_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    candles = await client.market_data.get_candles(
        figi=figi,
        from_=from_time,
        to=datetime.now(timezone.utc),
        interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
    )
    data = []
    for candle in candles.candles:
        data.append({
            "time": candle.time.isoformat(),
            "open": candle.open.units + candle.open.nano / 1e9,
            "high": candle.high.units + candle.high.nano / 1e9,
            "low": candle.low.units + candle.low.nano / 1e9,
            "close": candle.close.units + candle.close.nano / 1e9,
            "volume": candle.volume
        })
    if data:
        await save_to_redis(figi_id, data)
    else:
        last_data = await get_last_redis_data(figi_id)
        if last_data:
            await save_to_redis(figi_id, last_data)
            print(f"Данные заменились прошлым значением: {last_data}")
        else:
            print(f"Нет данных для figi_id: {figi_id} и отсутствуют прошлые данные в Redis")

async def fetch_and_store_data():
    async with AsyncClient(TOKEN) as client:
        while True:
            tasks = [fetch_data_for_figi(client, figi_id, figi) for figi_id, figi in figi_list.items()]
            await asyncio.gather(*tasks)
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(fetch_and_store_data())
