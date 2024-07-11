from flask import Flask, jsonify, request
import psycopg2
import json
from dotenv import load_dotenv
import os
import ta
import pandas as pd

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

def calculate_technical_indicators(df):
    indicators = {}

    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['stoch'] = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close']).stoch()
    df['stochrsi'] = ta.momentum.StochRSIIndicator(df['close']).stochrsi()
    df['macd'] = ta.trend.MACD(df['close']).macd()
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
    df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
    df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
    df['ult_osc'] = ta.momentum.UltimateOscillator(df['high'], df['low'], df['close']).ultimate_oscillator()
    df['roc'] = ta.momentum.ROCIndicator(df['close']).roc()
    df['bull_bear_power'] = df['close'] - ta.trend.EMAIndicator(df['close'], window=13).ema_indicator()

    indicators['rsi'] = df['rsi'].iloc[-1]
    indicators['stoch'] = df['stoch'].iloc[-1]
    indicators['stochrsi'] = df['stochrsi'].iloc[-1]
    indicators['macd'] = df['macd'].iloc[-1]
    indicators['adx'] = df['adx'].iloc[-1]
    indicators['williams_r'] = df['williams_r'].iloc[-1]
    indicators['cci'] = df['cci'].iloc[-1]
    indicators['atr'] = df['atr'].iloc[-1]
    indicators['ult_osc'] = df['ult_osc'].iloc[-1]
    indicators['roc'] = df['roc'].iloc[-1]
    indicators['bull_bear_power'] = df['bull_bear_power'].iloc[-1]

    return indicators

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

@app.route('/api/search', methods=['GET'])
def search_companies():
    query = request.args.get('query', default='', type=str)
    if query:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT figi_id, company_name 
            FROM figi_numbers 
            WHERE company_name ILIKE %s
            LIMIT 10;
        ''', (f'%{query}%',))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        results = [{'figi_id': row[0], 'company_name': row[1]} for row in rows]
        return jsonify(results)
    return jsonify([])

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

def aggregate_candles_query(time_frame):
    if time_frame == '1m':
        return '''
        SELECT
            time_of_candle AS bucket,
            open_price,
            low_price,
            high_price,
            close_price,
            volume
        FROM
            candles
        WHERE
            figi_id = %s
        ORDER BY
            bucket
        '''
    elif time_frame == '5m':
        interval = '5 minute'
    elif time_frame == '10m':
        interval = '10 minute'
    elif time_frame == '1h':
        interval = '1 hour'
    else:
        raise ValueError("Invalid time frame")

    return f'''
    SELECT
        date_trunc('{interval}', time_of_candle) AS bucket,
        first(open_price) OVER (PARTITION BY date_trunc('{interval}', time_of_candle) ORDER BY time_of_candle) AS open_price,
        MIN(low_price) AS low_price,
        MAX(high_price) AS high_price,
        last(close_price) OVER (PARTITION BY date_trunc('{interval}', time_of_candle) ORDER BY time_of_candle) AS close_price,
        SUM(volume) AS volume
    FROM
        candles
    WHERE
        figi_id = %s
    GROUP BY
        date_trunc('{interval}', time_of_candle)
    ORDER BY
        bucket
    '''

@app.route('/api/candles', methods=['GET'])
def get_candles():
    figi_id = request.args.get('figi_id', default=1, type=int)
    time_frame = request.args.get('time_frame', default='1m', type=str)

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query = aggregate_candles_query(time_frame)
        cur.execute(query, (figi_id,))
        rows = cur.fetchall()
        
        candles = []
        for row in rows:
            candles.append({
                'time': int(row[0].timestamp()),
                'open': float(row[1]),
                'low': float(row[2]),
                'high': float(row[3]),
                'close': float(row[4]),
                'volume': int(row[5])
            })

        cur.execute('SELECT company_name FROM figi_numbers WHERE figi_id = %s', (figi_id,))
        company_name = cur.fetchone()[0]
        
    finally:
        cur.close()
        conn.close()

    df = pd.DataFrame(candles)
    indicators = calculate_technical_indicators(df)

    return jsonify({'candles': candles, 'company_name': company_name, 'indicators': indicators})

if __name__ == '__main__':
    app.run(debug=True)
