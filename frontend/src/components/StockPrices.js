import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import '../styles/StockPrices.css';

const StockPrices = () => {
    const [prices, setPrices] = useState([]);
    const [companies, setCompanies] = useState([]);
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

        const fetchCompanies = async () => {
            try {
                const response = await axios.get('/api/company_list');
                const companyList = Object.entries(response.data).map(([name, details]) => ({
                    id: details.id,
                    name: name.charAt(0).toUpperCase() + name.slice(1)
                }));
                setCompanies(companyList);
            } catch (error) {
                console.error('Error fetching company list:', error);
            }
        };

        fetchPrices();
        fetchCompanies();
        const intervalId = setInterval(fetchPrices, 60000); 

        return () => clearInterval(intervalId);
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
                    <div
                        key={company.id}
                        className="price-item"
                        id={`price-${company.id}`}
                    >
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
