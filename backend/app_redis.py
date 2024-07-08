from flask import Flask, jsonify, request, Response
import json
from dotenv import load_dotenv
import redis
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

figi_list = {
    1: ("BBG004731032", "Лукойл"),
    2: ("BBG004731354", "Роснефть"),
    3: ("BBG004730ZJ9", "ВТБ"),
    4: ("BBG004730RP0", "Газпром"),
    5: ("BBG004S681W1", "МТС"),
    6: ("BBG004730N88", "Сбербанк"),
    7: ("BBG00475KKY8", "Новатэк"),
    8: ("BBG004S68473", "Интер РАО"),
    9: ("BBG0047315D0", "Сургутнефтегаз"),
    10: ("BBG004S68614", "АФК Система")
}

def get_candles_for_figi(figi_id):
    today = datetime.now().date().isoformat()
    pattern = f"{figi_id}_{'_'.join(str(today).split('-'))}_*"
    keys = redis_client.keys(pattern)

    if not keys:
        return None, None, 0

    keys.sort()
    first_candle = None
    last_candle = None
    total_volume = 0

    for key in keys:
        data = redis_client.get(key)
        if data:
            candle = json.loads(data)[0]
            total_volume += candle['volume']
            if first_candle is None:
                first_candle = candle
            last_candle = candle

    return first_candle, last_candle, total_volume

@app.route('/api/top_volume', methods=['GET'])
def get_top_volume():
    cache_key = "top_volume"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))

    top_volume = []

    for figi_id, (figi, company_name) in figi_list.items():
        first_candle, last_candle, total_volume = get_candles_for_figi(figi_id)

        if first_candle and last_candle:
            top_volume.append({
                'figi_id': figi_id,
                'company_name': company_name,
                'total_volume': total_volume,
                'percentage_change': ((last_candle['close'] - first_candle['close']) / first_candle['close']) * 100
            })

    top_volume.sort(key=lambda x: x['total_volume'], reverse=True)
    top_volume = top_volume[:10]

    # Cache the response data
    redis_client.setex(cache_key, timedelta(minutes=10), json.dumps(top_volume))

    return jsonify(top_volume)

@app.route('/api/candles', methods=['GET'])
def get_candles():
    figi_id = request.args.get('figi_id', default=1, type=int)
    
    if figi_id not in figi_list:
        return jsonify({'error': 'Invalid figi_id'}), 400
    
    figi, company_name = figi_list[figi_id]

    cache_key = f"candles_{figi_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return Response(cached_data, content_type='application/json; charset=utf-8')

    pattern = f"{figi_id}_*"
    keys = redis_client.keys(pattern)
    
    if not keys:
        return jsonify({'error': 'No data found'}), 404
    
    keys.sort()
    candles = []
    
    for key in keys:
        data = redis_client.get(key)
        if data:
            candle = json.loads(data)[0]
            dt = datetime.fromisoformat(candle["time"])
            dt_plus_3_hours = dt + timedelta(hours=3)
            timestamp_plus_3_hours = int(dt_plus_3_hours.timestamp())
            candles.append({
                'time': timestamp_plus_3_hours,
                'open': candle['open'],
                'low': candle['low'],
                'high': candle['high'],
                'close': candle['close'],
                'volume': candle['volume'],
            })
    
    candles.sort(key=lambda x: x['time'])
    response_data = json.dumps({'candles': candles, 'company_name': company_name}, ensure_ascii=False, indent=4)
    
    # Cache the response data
    redis_client.setex(cache_key, timedelta(minutes=10), response_data)

    response = Response(response_data, content_type='application/json; charset=utf-8')
    print({'candles': candles, 'company_name': company_name})
    return response



@app.route('/api/top_gainers', methods=['GET'])
def get_top_gainers():
    cache_key = "top_gainers"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))

    top_gainers = []

    for figi_id, (figi, company_name) in figi_list.items():
        first_candle, last_candle, total_volume = get_candles_for_figi(figi_id)

        if first_candle and last_candle:
            percentage_change = ((last_candle['close'] - first_candle['close']) / first_candle['close']) * 100
            if percentage_change > 0:
                top_gainers.append({
                    'figi_id': figi_id,
                    'company_name': company_name,
                    'percentage_change': percentage_change
                })

    top_gainers.sort(key=lambda x: x['percentage_change'], reverse=True)
    top_gainers = top_gainers[:10]

    # Cache the response data
    redis_client.setex(cache_key, timedelta(minutes=10), json.dumps(top_gainers))

    return jsonify(top_gainers)

@app.route('/api/top_losers', methods=['GET'])
def get_top_losers():
    cache_key = "top_losers"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))

    top_losers = []

    for figi_id, (figi, company_name) in figi_list.items():
        first_candle, last_candle, total_volume = get_candles_for_figi(figi_id)

        if first_candle and last_candle:
            percentage_change = ((last_candle['close'] - first_candle['close']) / first_candle['close']) * 100
            if percentage_change < 0:
                top_losers.append({
                    'figi_id': figi_id,
                    'company_name': company_name,
                    'percentage_change': percentage_change
                })

    top_losers.sort(key=lambda x: x['percentage_change'])
    top_losers = top_losers[:10]

    # Cache the response data
    redis_client.setex(cache_key, timedelta(minutes=10), json.dumps(top_losers))

    return jsonify(top_losers)


if __name__ == '__main__':
    app.run(debug=True)
