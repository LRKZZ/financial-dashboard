import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { createChart } from 'lightweight-charts';
import './ChartComponent.css';

const companyColors = {
    1: '#4caf50', // ЛУКОЙЛ - зеленый
    2: '#ff5722', // Роснефть - красный
    3: '#2196f3', // ВТБ - синий
    4: '#ffeb3b', // Газпром - желтый
    5: '#9c27b0', // МТС - фиолетовый
    6: '#3f51b5', // Сбербанк - индиго
    7: '#ff9800', // Новатэк - оранжевый
    8: '#00bcd4', // Интер РАО - голубой
    9: '#e91e63', // Сургутнефтегаз - розовый
    10: '#795548' // АФК Система - коричневый
};

function ChartComponent() {
    const { figi_id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState([]);
    const [companyName, setCompanyName] = useState('');
    const [lastPrice, setLastPrice] = useState(null);
    const [priceChangeClass, setPriceChangeClass] = useState('');
    const [indicators, setIndicators] = useState({});
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const candleSeriesRef = useRef();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await axios.get(`/api/candles?figi_id=${figi_id}`);
                setData(result.data.candles);
                setCompanyName(result.data.company_name);
                setIndicators(result.data.indicators);

                const newPrice = result.data.candles[result.data.candles.length - 1].close;

                if (lastPrice !== null) {
                    if (newPrice > lastPrice) {
                        setPriceChangeClass('price-up');
                    } else if (newPrice < lastPrice) {
                        setPriceChangeClass('price-down');
                    } else {
                        setPriceChangeClass('');
                    }
                }

                setLastPrice(newPrice);

                if (!chartRef.current) {
                    // Initialize chart
                    const chartProperties = {
                        width: chartContainerRef.current.clientWidth,
                        height: 400,
                        timeScale: {
                            timeVisible: true,
                            secondsVisible: false,
                        },
                        layout: {
                            backgroundColor: '#ffffff',
                            textColor: '#000000',
                        }
                    };

                    const domElement = chartContainerRef.current;
                    chartRef.current = createChart(domElement, chartProperties);
                    candleSeriesRef.current = chartRef.current.addCandlestickSeries();

                    candleSeriesRef.current.setData(result.data.candles.map(item => ({
                        time: item.time,
                        open: item.open,
                        high: item.high,
                        low: item.low,
                        close: item.close
                    })));
                } else {
                    candleSeriesRef.current.setData(result.data.candles.map(item => ({
                        time: item.time,
                        open: item.open,
                        high: item.high,
                        low: item.low,
                        close: item.close
                    })));
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();

        const intervalId = setInterval(fetchData, 60000); // Fetch data every minute

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, [figi_id, lastPrice]);

    useEffect(() => {
        if (priceChangeClass) {
            const timeoutId = setTimeout(() => {
                setPriceChangeClass('');
            }, 1000); // Remove animation class after 1 second
            return () => clearTimeout(timeoutId);
        }
    }, [priceChangeClass]);

    const getRecommendation = () => {
        const buyIndicators = ['macd', 'cci', 'roc', 'ult_osc'];
        const sellIndicators = ['rsi', 'stoch', 'stochrsi', 'adx', 'williams_r'];

        let buyCount = 0;
        let sellCount = 0;

        buyIndicators.forEach(indicator => {
            if (indicators[indicator] > 0) buyCount++;
        });

        sellIndicators.forEach(indicator => {
            if (indicators[indicator] < 0) sellCount++;
        });

        if (buyCount > sellCount) {
            return { recommendation: 'Активно покупать', color: 'green' };
        } else if (sellCount > buyCount) {
            return { recommendation: 'Продавать', color: 'red' };
        } else {
            return { recommendation: 'Держать', color: 'gray' };
        }
    };

    const recommendation = getRecommendation();

    return (
        <div className="chart-component">
            <div className="navbar">
                <button onClick={() => navigate('/')}>Топ по обороту</button>
                <button onClick={() => navigate('/')}>Взлеты дня</button>
                <button onClick={() => navigate('/')}>Падения дня</button>
                <button onClick={() => navigate('/')}>Главное меню</button>
            </div>
            <div className="company-header" style={{ backgroundColor: companyColors[figi_id] }}>
                <div className="company-info">
                    <h1 className="company-name">{companyName}</h1>
                    <p className="company-sector">Сектор: Финансовый сектор</p>
                </div>
                <img src={`/company_logos/${figi_id}.1.png`} alt={`${companyName} logo`} className="company-logo" />
            </div>
            <div className="price-section">
                <h2 className={`price-display ${priceChangeClass}`}>{lastPrice}₽</h2>
            </div>
            <div className="chart-container" ref={chartContainerRef}></div>
            <div className="technical-indicators">
                <div className="technical-summary" style={{ color: recommendation.color }}>
                    <h3>Тех. индикаторы</h3>
                    <p>{recommendation.recommendation}</p>
                </div>
                <table className="technical-table">
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Значение</th>
                            <th>Действие</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(indicators).map(([name, value]) => (
                            <tr key={name}>
                                <td>{name}</td>
                                <td>{value.toFixed(4)}</td>
                                <td>{value > 0 ? 'Покупать' : 'Продавать'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ChartComponent;
