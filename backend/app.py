from flask import Flask, request
import redis
from queries.get_top_gainers import get_top_gainers
from queries.get_top_volume import get_top_volume
from queries.get_top_losers import get_top_losers
from queries.get_top_gainers import get_top_gainers
from queries.get_search_company import search_company
from queries.get_lastest_prices import get_latest_prices
from queries.get_candles import get_candle
from queries.get_currency_rates import get_currency_rates
from queries.get_top_decline import get_top_decline
from queries.get_top_growth import get_top_growth
from queries.get_company_list import get_company_list

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

app = Flask(__name__)


@app.route("/api/top_volume", methods=["GET"])
def top_volume():
    return get_top_volume()


@app.route("/api/top_gainers", methods=["GET"])
def top_gainers():
    return get_top_gainers()


@app.route("/api/top_losers", methods=["GET"])
def top_losers():
    return get_top_losers()


@app.route("/api/search", methods=["GET"])
def search_companies():
    query = request.args.get("query", default="", type=str)
    return search_company(query)


@app.route("/api/candles", methods=["GET"])
def get_candles():
    figi_id = request.args.get("figi_id", default=1, type=int)
    time_frame = request.args.get("time_frame", default="1m", type=str)
    return get_candle(figi_id, time_frame)


@app.route("/api/latest_prices", methods=["GET"])
def get_prices():
    return get_latest_prices()


@app.route("/api/currency_rates", methods=["GET"])
def get_currency():
    return get_currency_rates()


@app.route('/api/top_decline', methods=['GET'])
def get_top_declines():
    return get_top_decline()


@app.route('/api/top_growth', methods=['GET'])
def get_top_growths():
    return get_top_growth()
    

@app.route('/api/company_list', methods=['GET'])
def company_list():
    return get_company_list()


if __name__ == "__main__":
    app.run(debug=True)
