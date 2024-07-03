import os
from datetime import timedelta
import asyncio
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType, LongType, TimestampType
from pyspark.sql import Row

token = "t.4-0QUkKqbdomKc3vNLAKQ4OdihFkqEcJvSjOmUwWsEwb4Kliu1PLMPKl2eGGBo9SfMbzNMNcBQqYIC5MbA13rQ"

async def fetch_data():
    data = []
    async with AsyncClient(token) as client:
        async for candle in client.get_all_candles(
            figi="BBG004730N88",
            from_=now() - timedelta(minutes=10),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            data.append([
                candle.time,
                candle.open.units + candle.open.nano / 1e9,
                candle.high.units + candle.high.nano / 1e9,
                candle.low.units + candle.low.nano / 1e9,
                candle.close.units + candle.close.nano / 1e9,
                candle.volume
            ])
    return data

async def stream_data(spark):
    schema = StructType([
        StructField("time", TimestampType(), True),
        StructField("open", DoubleType(), True),
        StructField("high", DoubleType(), True),
        StructField("low", DoubleType(), True),
        StructField("close", DoubleType(), True),
        StructField("volume", LongType(), True)
    ])
    
    count = 0

    while True:
        data = await fetch_data()
        count += 1

        new_df = spark.createDataFrame(data, schema)

        print(f"Received batch number: {count}")
        new_df.show()

        await asyncio.sleep(60)

async def main():
    spark = SparkSession.builder \
        .appName("Tinkoff Invest Data Streaming") \
        .config("spark.local.dir", "C:/tmp/spark-temp") \
        .getOrCreate()

    await stream_data(spark)

if __name__ == "__main__":
    asyncio.run(main())
