from flask import Flask, jsonify, request
import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv()

PASSWORD = os.getenv("PASSWORD_SQL")

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname="financial_db",
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432"
    )
    return conn

@app.route('/api/top_volume', methods=['GET'])
def get_top_volume():
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
    return jsonify(top_volume)

@app.route('/api/top_gainers', methods=['GET'])
def get_top_gainers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    WITH daily_prices AS (
        SELECT 
            c.figi_id,
            f.company_name,
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
        percentage_change
    FROM
        price_changes
    WHERE
        percentage_change > 0
    ORDER BY
        percentage_change DESC
    LIMIT 10;
    ''')
    rows = cur.fetchall()
    top_gainers = []
    for row in rows:
        top_gainers.append({
            'figi_id': row[0],
            'company_name': row[1],
            'percentage_change': float(row[2]) 
        })
    cur.close()
    conn.close()
    return jsonify(top_gainers)

@app.route('/api/top_losers', methods=['GET'])
def get_top_losers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    WITH daily_prices AS (
        SELECT 
            c.figi_id,
            f.company_name,
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
        percentage_change
    FROM
        price_changes
    WHERE
        percentage_change < 0
    ORDER BY
        percentage_change ASC
    LIMIT 10;
    ''')
    rows = cur.fetchall()
    top_losers = []
    for row in rows:
        top_losers.append({
            'figi_id': row[0],
            'company_name': row[1],
            'percentage_change': float(row[2]) 
        })
    cur.close()
    conn.close()
    return jsonify(top_losers)

@app.route('/api/candles', methods=['GET'])
def get_candles():
    figi_id = request.args.get('figi_id', default=1, type=int)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT time_of_candle, open_price, low_price, high_price, close_price FROM candles WHERE figi_id = %s ORDER BY time_of_candle ASC', (figi_id,))
    rows = cur.fetchall()
    candles = []
    for row in rows:
        candles.append({
            'time': row[0].timestamp(),
            'open': float(row[1]),
            'low': float(row[2]),
            'high': float(row[3]),
            'close': float(row[4])
        })
    cur.execute('SELECT company_name FROM figi_numbers WHERE figi_id = %s', (figi_id,))
    company_name = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({'candles': candles, 'company_name': company_name})

if __name__ == '__main__':
    app.run(debug=True)
