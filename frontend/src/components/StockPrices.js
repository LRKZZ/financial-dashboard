import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import '../styles/StockPrices.css';

const companies = [
    { id: 1, name: 'ЛУКОЙЛ' },
    { id: 2, name: 'Роснефть' },
    { id: 3, name: 'ВТБ' },
    { id: 4, name: 'Газпром' },
    { id: 5, name: 'МТС' },
    { id: 6, name: 'Сбербанк' },
    { id: 7, name: 'Новатэк' },
    { id: 8, name: 'Интер РАО' },
    { id: 9, name: 'Сургутнефтегаз' },
    { id: 10, name: 'АФК Система' },
];

const StockPrices = () => {
    const [prices, setPrices] = useState([]);
    const previousPrices = useRef({});

    useEffect(() => {
        const fetchPrices = async () => {
            try {
                const result = await axios.get('/api/latest_prices');
                setPrices(result.data);
            } catch (error) {
                console.error('Error fetching stock prices:', error);
            }
        };

        fetchPrices();
        const intervalId = setInterval(fetchPrices, 60000); // Fetch prices every minute

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, []);

    useEffect(() => {
        prices.forEach(price => {
            if (previousPrices.current[price.figi_id] !== undefined) {
                if (previousPrices.current[price.figi_id] < price.close_price) {
                    document.getElementById(`price-${price.figi_id}`).classList.add('price-up');
                    setTimeout(() => {
                        document.getElementById(`price-${price.figi_id}`).classList.remove('price-up');
                    }, 1500);
                } else if (previousPrices.current[price.figi_id] > price.close_price) {
                    document.getElementById(`price-${price.figi_id}`).classList.add('price-down');
                    setTimeout(() => {
                        document.getElementById(`price-${price.figi_id}`).classList.remove('price-down');
                    }, 1500);
                }
            }
            previousPrices.current[price.figi_id] = price.close_price;
        });
    }, [prices]);

    const getPriceForCompany = (figi_id) => {
        const priceData = prices.find(price => price.figi_id === figi_id);
        return priceData ? priceData.close_price : 'Загрузка...';
    };

    return (
        <div className="stock-prices">
            <h2 className="latest-prices-title">Последние цены акций</h2>
            <div className="prices-grid">
                {companies.map(company => (
                    <div key={company.id} className="price-item" id={`price-${company.id}`}>
                        <div className="company-info">
                            <span className="company-name">{company.name}</span>
                            <span className="company-price">{getPriceForCompany(company.id)} ₽</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StockPrices;
