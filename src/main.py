import asyncio
from data_processing import stream_data

async def main():
    await stream_data()

if __name__ == "__main__":
    asyncio.run(main())
