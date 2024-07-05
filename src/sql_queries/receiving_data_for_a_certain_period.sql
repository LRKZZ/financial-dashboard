CREATE OR REPLACE FUNCTION get_candle_data(rnk_limit INTEGER)
RETURNS TABLE (
    figi_id SMALLINT,
    first_open_price NUMERIC,
    last_close_price NUMERIC,
    min_low_price NUMERIC,
    max_high_price NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH ranked_candles AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY c.figi_id ORDER BY c.time_of_candle DESC) as rnk
        FROM candles c
        WHERE c.time_of_candle <= NOW()
    ),
    last_five AS (
        SELECT *
        FROM ranked_candles rf
        WHERE rf.rnk <= rnk_limit
    ),
    first_open AS (
        SELECT DISTINCT ON (rf.figi_id) rf.figi_id, rf.open_price
        FROM last_five rf
        ORDER BY rf.figi_id, rf.time_of_candle ASC
    ),
    last_close AS (
        SELECT DISTINCT ON (rf.figi_id) rf.figi_id, rf.close_price
        FROM last_five rf
        ORDER BY rf.figi_id, rf.time_of_candle DESC
    )
    SELECT 
        l.figi_id,
        fo.open_price AS first_open_price,
        lc.close_price AS last_close_price,
        MIN(l.low_price) AS min_low_price,
        MAX(l.high_price) AS max_high_price
    FROM last_five l
    JOIN first_open fo ON l.figi_id = fo.figi_id
    JOIN last_close lc ON l.figi_id = lc.figi_id
    GROUP BY l.figi_id, fo.open_price, lc.close_price;
END;
$$ LANGUAGE plpgsql;
