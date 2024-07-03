from datetime import timedelta
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("TOKEN")

def get_timedelta(interval):
    if interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
        return timedelta(minutes=10)
    elif interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
        return timedelta(minutes=5 * 10)
    elif interval == CandleInterval.CANDLE_INTERVAL_10_MIN:
        return timedelta(minutes=10 * 10)
    elif interval == CandleInterval.CANDLE_INTERVAL_HOUR:
        return timedelta(hours=10)
    elif interval == CandleInterval.CANDLE_INTERVAL_DAY:
        return timedelta(days=10)
    else:
        raise ValueError("Unsupported interval")

async def fetch_data(token, figi, interval):
    data = []
    async with AsyncClient(token) as client:
        async for candle in client.get_all_candles(
            figi=figi,
            from_=now() - get_timedelta(interval),
            interval=interval,
        ):
            data.append([
                candle.time,
                candle.open.units + candle.open.nano / 1e9,
                candle.high.units + candle.high.nano / 1e9,
                candle.low.units + candle.low.nano / 1e9,
                candle.close.units + candle.close.nano / 1e9,
                candle.volume
            ])
    return data
