from queries.get_aggregate_candles_query import aggregate_candles_query
from queries.get_tehnical_indicatords import calculate_technical_indicators
from connection.get_db_connection import get_db_connection
from flask import jsonify
import pandas as pd
from sqlalchemy import create_engine, text
import os 


DATABASE_URL = f"postgresql://postgres:{os.getenv('PASSWORD_SQL')}@localhost:5432/financial_db"

def get_candle(figi_id, time_frame):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        query = aggregate_candles_query(time_frame)
        result = conn.execute(text(query), {"figi_id": figi_id})
        rows = result.fetchall()

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

        result = conn.execute(text("SELECT company_name FROM figi_numbers WHERE figi_id = :figi_id"), {"figi_id": figi_id})
        company_name = result.fetchone()[0]

    if time_frame == "1m": 
        df = pd.DataFrame(candles)
        indicators = calculate_technical_indicators(df)
    else:
        indicators = {indicator: 0 for indicator in [
            'rsi', 'stoch', 'stochrsi', 'macd', 'adx', 'williams_r', 'cci', 'atr', 'ult_osc', 'roc', 'bull_bear_power'
        ]}

    return jsonify(
        {"candles": candles, "company_name": company_name, "indicators": indicators}
    )
