import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles/CurrencyRates.css';

const CurrencyRates = () => {
    const [rates, setRates] = useState({ usd: null, eur: null });
    const [dateTime, setDateTime] = useState(new Date());

    useEffect(() => {
        const fetchRates = async () => {
            try {
                const result = await axios.get('/api/currency_rates');
                setRates(result.data);
            } catch (error) {
                console.error('Error fetching currency rates:', error);
            }
        };

        fetchRates();
        const intervalId = setInterval(fetchRates, 60000); // Fetch rates every minute

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, []);

    useEffect(() => {
        const updateDateTime = () => {
            setDateTime(new Date());
        };

        const intervalId = setInterval(updateDateTime, 1000); // Update date and time every second

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, []);

    return (
        <div className="currency-rates">
            <h3>Курсы валют</h3>
            <div className="rate-item">
                <span className="currency-name">USD:</span>
                <span className="currency-rate">{rates.usd ? `${rates.usd} ₽` : 'Загрузка...'}</span>
            </div>
            <div className="rate-item">
                <span className="currency-name">EUR:</span>
                <span className="currency-rate">{rates.eur ? `${rates.eur} ₽` : 'Загрузка...'}</span>
            </div>
            <div className="rate-item">
                <span className="additional-info">Дата и время:</span>
                <span className="date-time">{dateTime.toLocaleString()}</span>
            </div>
        </div>
    );
};

export default CurrencyRates;
