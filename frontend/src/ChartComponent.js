import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
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
    const location = useLocation();
    const [data, setData] = useState([]);
    const [companyName, setCompanyName] = useState('');
    const [lastPrice, setLastPrice] = useState(null);
    const [priceChangeClass, setPriceChangeClass] = useState('');
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const candleSeriesRef = useRef();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await axios.get(`/api/candles?figi_id=${figi_id}`);
                setData(result.data.candles);
                setCompanyName(result.data.company_name);

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

    return (
        <div className="chart-component">
            <div className="navbar">
                <button className={location.pathname === '/' ? 'active' : ''} onClick={() => navigate('/')}>Топ по обороту</button>
                <button className={location.pathname === '/' ? 'active' : ''} onClick={() => navigate('/')}>Взлеты дня</button>
                <button className={location.pathname === '/' ? 'active' : ''} onClick={() => navigate('/')}>Падения дня</button>
                <button className={location.pathname === '/' ? 'active' : ''} onClick={() => navigate('/')}>Главное меню</button>
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
        </div>
    );
}

export default ChartComponent;
