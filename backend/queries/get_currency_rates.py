import requests
from flask import jsonify
import os

API_KEY = os.getenv("CURRENCY_API")

def get_currency_rates():
    try:
        response = requests.get(f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD')
        data = response.json()
        usd_to_rub = data['conversion_rates']['RUB']
        
        response = requests.get(f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/EUR')
        data = response.json()
        eur_to_rub = data['conversion_rates']['RUB']
        
        rates = {
            "usd": usd_to_rub,
            "eur": eur_to_rub
        }
        return jsonify(rates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500