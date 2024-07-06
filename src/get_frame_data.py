import redis
import datetime
import json

client = redis.StrictRedis(host="localhost", port=6379, db=0)
keys = list(map(lambda key: key.decode("utf-8").split("_"), client.keys("*")))

# Обработка ключей из redis
data = {i: [] for i in range(1, 11)}

for key in keys:
    key_converted = list(map(lambda x: int(x), key))
    figi_id = key_converted[0]
    date = datetime.datetime(*key_converted[1:])
    redis_key = "_".join(key)
    
    data[figi_id].append((date, redis_key))

# Основная функция получения данных
def receiving_data_for_n_interval(data: dict, figi_id: int, minutes: int) -> dict:
    keys_n_minutes = sorted(data[figi_id], key=lambda x: x[0])[:minutes]

    avg_candle = {
        "time": [],
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": []
    }

    for key in keys_n_minutes:
        value = client.get(key[1])
        print(value)
        value_dict = json.loads(value.decode("utf-8"))
        avg_candle['open'].append(value_dict['open'])
        avg_candle['high'].append(value_dict['high'])
        avg_candle['low'].append(value_dict['low'])
        avg_candle['close'].append(value_dict['close'])
        avg_candle['volume'].append(value_dict['volume'])

    return {
            "first_open": avg_candle["open"][0], 
            "max_high": max(avg_candle["high"]),
            "min_low": min(avg_candle["low"]), 
            "last_close": avg_candle["close"][-1],
            "sum_volume": sum(avg_candle["volume"])
        }

result = receiving_data_for_n_interval(data, figi_id=6, minutes=10)
print(result)
