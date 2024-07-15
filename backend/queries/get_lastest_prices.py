from connection.get_db_connection import get_db_connection
from flask import jsonify
import redis
import json
from datetime import timedelta


redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)


def get_latest_prices():
    cache_key = "latest_prices"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT figi_id, close_price 
        FROM (
            SELECT figi_id, close_price, ROW_NUMBER() OVER (PARTITION BY figi_id ORDER BY time_of_candle DESC) as rn
            FROM candles
        ) subquery
        WHERE rn = 1
        LIMIT 10;
        """
    )

    rows = cur.fetchall()
    latest_prices = []
    for row in rows:
        latest_prices.append(
            {
                "figi_id": row[0],
                "close_price": float(row[1])
            }
        )
    cur.close()
    conn.close()

    redis_client.setex(cache_key, timedelta(minutes=1), json.dumps(latest_prices))

    return jsonify(latest_prices)
