def aggregate_candles_query(time_frame):

    tables_by_time = {
        "1m": "candles",
        "5m": "candles_5_min",
        "10m": "candles_10_min",
        "1h": "candles_60_min"
    }

    print(time_frame)
    return f"""
    SELECT
        time_of_candle AS bucket,
        open_price,
        low_price,
        high_price,
        close_price,
        volume
    FROM
        {tables_by_time[time_frame]}
    WHERE
        figi_id = %s
    ORDER BY
        bucket
    """
