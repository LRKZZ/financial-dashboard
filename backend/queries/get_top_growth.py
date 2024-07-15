from connection.get_db_connection import get_db_connection
from flask import jsonify
from datetime import timedelta
import json
import redis

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)


def get_top_decline():
    cache_key = "top_decline"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
    WITH first_last_prices AS (
        SELECT
            figi_id,
            FIRST_VALUE(close_price) OVER (PARTITION BY figi_id ORDER BY time_of_candle ASC) AS first_close_price,
            LAST_VALUE(close_price) OVER (PARTITION BY figi_id ORDER BY time_of_candle ASC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_close_price
        FROM
            candles
    ),
    price_changes AS (
        SELECT
            flp.figi_id,
            f.company_name,
            ((flp.last_close_price - flp.first_close_price) / flp.first_close_price * 100) AS growth_percentage
        FROM
            first_last_prices flp
        JOIN
            figi_numbers f ON flp.figi_id = f.figi_id
        WHERE
            ((flp.last_close_price - flp.first_close_price) / flp.first_close_price * 100) > 0
    )
    SELECT
        figi_id,
        company_name,
        growth_percentage
    FROM
        price_changes
    ORDER BY
        growth_percentage DESC
    LIMIT 10;
    """
    )
    rows = cur.fetchall()
    top_growth = []
    for row in rows:
        top_growth.append(
            {
                "figi_id": row[0],
                "company_name": row[1],
                "percentage_change": float(row[2]),
            }
        )
    cur.close()
    conn.close()

    redis_client.setex(cache_key, timedelta(minutes=1), json.dumps(top_growth))

    return jsonify(top_growth)
