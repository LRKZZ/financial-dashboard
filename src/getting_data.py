import os
from dotenv import load_dotenv
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from tinkoff.invest import AsyncClient, CandleInterval
import json
import sys
import redis.asyncio as redis

# Загрузка токена из файла .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

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

class AsyncCustomIndex:
    def __init__(self, token, figi_list, redis_host, redis_port):
        self.token = token
        self.figi_list = figi_list
        self.redis_client = redis.from_url(f"redis://{redis_host}:{redis_port}")
        self.logger = self.__create_logger()

    def __create_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('--> %(asctime)s - %(name)s - %(levelname)s - %(message)s')

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        return logger

    async def fetch_candle(self, client, figi):
        try:
            now = datetime.now(timezone.utc)
            from_ = now - timedelta(minutes=1)
            to_ = now  
            candles = await client.market_data.get_candles(
                figi=figi,
                from_=from_,
                to=to_,
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN
            )
            return candles.candles[-1] if candles.candles else None
        except Exception as e:
            self.logger.exception(e)

    async def get_previous_data(self, figi_number):
        pattern = f"{figi_number}_*"
        keys = await self.redis_client.keys(pattern)
        if keys:
            latest_key = max(keys)
            latest_data = await self.redis_client.get(latest_key)
            return json.loads(latest_data)
        return None

    async def process_figi(self, client, figi_number, figi):
        candle = await self.fetch_candle(client, figi)
        if candle:
            data = {
                "time": candle.time.isoformat(),
                "open": candle.open.units + candle.open.nano / 1e9,
                "high": candle.high.units + candle.high.nano / 1e9,
                "low": candle.low.units + candle.low.nano / 1e9,
                "close": candle.close.units + candle.close.nano / 1e9,
                "volume": candle.volume
            }
        else:
            self.logger.info(f"No new data for {figi}. Fetching previous data.")
            data = await self.get_previous_data(figi_number)
            if data:
                data['time'] = datetime.now(timezone.utc).isoformat()
        
        if data:  # Проверяем, что data не None перед использованием
            key = f"{figi_number}_{datetime.now(timezone.utc).strftime('%Y_%m_%d_%H_%M_%S')}"
            await self.redis_client.set(key, json.dumps(data))
            self.logger.info(f"Data for {figi_number} stored in Redis with key {key}")

    async def stream_data(self):
        async with AsyncClient(self.token) as client:
            while True:
                tasks = [self.process_figi(client, figi_number, figi) for figi_number, figi in self.figi_list.items()]
                await asyncio.gather(*tasks)
                await asyncio.sleep(60)

async def main():
    index = AsyncCustomIndex(TOKEN, figi_list, REDIS_HOST, REDIS_PORT)
    await index.stream_data()

if __name__ == "__main__":
    asyncio.run(main())
