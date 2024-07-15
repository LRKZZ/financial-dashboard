from queries.get_aggregate_candles_query import aggregate_candles_query
from queries.get_tehnical_indicatords import calculate_technical_indicators
from connection.get_db_connection import get_db_connection
from flask import jsonify
import pandas as pd


def get_candle(figi_id, time_frame):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        query = aggregate_candles_query(time_frame)
        cur.execute(query, (figi_id,))
        rows = cur.fetchall()

        candles = []
        for row in rows:
            candles.append(
                {
                    "time": int(row[0].timestamp()),
                    "open": float(row[1]),
                    "low": float(row[2]),
                    "high": float(row[3]),
                    "close": float(row[4]),
                    "volume": int(row[5]),
                }
            )

        cur.execute(
            "SELECT company_name FROM figi_numbers WHERE figi_id = %s", (figi_id,)
        )
        company_name = cur.fetchone()[0]

    finally:
        cur.close()
        conn.close()

    if time_frame == "1h":
        df = pd.DataFrame(candles)
        indicators = calculate_technical_indicators(df)
    else:
        indicators = {indicator: 0 for indicator in [
                'rsi', 'stoch', 'stochrsi', 'macd', 'adx', 'williams_r', 'cci', 'atr', 'ult_osc', 'roc', 'bull_bear_power'
            ]}

    return jsonify(
        {"candles": candles, "company_name": company_name, "indicators": indicators}
    )
