from config import redis_client

def cache_candle_data(figi, data):
    key = f"candle_data:{figi}"
    redis_client.set(key, str(data), ex=60)  # Кэширование данных на 60 секунд

def get_cached_candle_data(figi):
    key = f"candle_data:{figi}"
    cached_data = redis_client.get(key)
    if cached_data:
        return eval(cached_data)
    return None
