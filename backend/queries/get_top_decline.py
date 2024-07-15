from flask import jsonify
from connection.get_db_connection import get_db_connection
import redis
from datetime import timedelta
import json

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

def get_top_decline():
    
    cache_key = "top_decline"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    WITH first_last_prices AS (
        SELECT
            figi_id,
            MIN(time_of_candle) AS first_time,
            MAX(time_of_candle) AS last_time
        FROM
            candles
        GROUP BY
            figi_id
    ),
    price_changes AS (
        SELECT
            flp.figi_id,
            f.company_name,
            ((last_price.close_price - first_price.close_price) / first_price.close_price * 100) AS growth_percentage
        FROM
            first_last_prices flp
        JOIN
            candles first_price ON flp.figi_id = first_price.figi_id AND flp.first_time = first_price.time_of_candle
        JOIN
            candles last_price ON flp.figi_id = last_price.figi_id AND flp.last_time = last_price.time_of_candle
        JOIN
            figi_numbers f ON flp.figi_id = f.figi_id
        WHERE
            first_price.close_price IS NOT NULL AND last_price.close_price IS NOT NULL
    )
    SELECT
        figi_id,
        company_name,
        growth_percentage
    FROM
        price_changes
    WHERE
        growth_percentage < 0
    ORDER BY
        growth_percentage ASC
    LIMIT 10;
    ''')
    rows = cur.fetchall()
    top_decline = []
    for row in rows:
        top_decline.append({
            'figi_id': row[0],
            'company_name': row[1],
            'percentage_change': float(row[2])
        })
    cur.close()
    conn.close()
    
    redis_client.setex(cache_key, timedelta(minutes=1), json.dumps(top_decline))
    
    return jsonify(top_decline)
