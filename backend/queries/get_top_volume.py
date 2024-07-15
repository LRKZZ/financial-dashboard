from flask import jsonify
from connection.get_db_connection import get_db_connection
import json
from datetime import timedelta
import redis

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)


def get_top_volume():

    cache_key = "top_volume"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    WITH daily_prices AS (
        SELECT 
            c.figi_id,
            f.company_name,
            SUM(c.volume) as total_volume,
            MIN(c.time_of_candle) AS first_time,
            MAX(c.time_of_candle) AS last_time
        FROM 
            candles c
        JOIN
            figi_numbers f ON c.figi_id = f.figi_id
        WHERE 
            date_trunc('day', c.time_of_candle) = current_date
        GROUP BY 
            c.figi_id, f.company_name
    ),
    price_changes AS (
        SELECT
            dp.figi_id,
            dp.company_name,
            dp.total_volume,
            (last_price.close_price - first_price.close_price) / first_price.close_price * 100 AS percentage_change
        FROM
            daily_prices dp
        JOIN
            candles first_price ON dp.figi_id = first_price.figi_id AND dp.first_time = first_price.time_of_candle
        JOIN
            candles last_price ON dp.figi_id = last_price.figi_id AND dp.last_time = last_price.time_of_candle
    )
    SELECT
        figi_id,
        company_name,
        total_volume,
        percentage_change
    FROM
        price_changes
    ORDER BY 
        total_volume DESC
    LIMIT 10;
    ''')
    rows = cur.fetchall()
    top_volume = []
    for row in rows:
        top_volume.append({
            'figi_id': row[0],
            'company_name': row[1],
            'total_volume': int(row[2]), 
            'percentage_change': float(row[3])  
        })
    cur.close()
    conn.close()

    redis_client.setex(cache_key, timedelta(minutes=1), json.dumps(top_volume))

    return jsonify(top_volume)