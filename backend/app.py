from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    # Генерация данных
    data = [
        {"time_of_candle": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'), "open_price": 7000 + i * 10}
        for i in range(10)
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
