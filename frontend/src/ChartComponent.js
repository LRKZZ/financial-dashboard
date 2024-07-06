import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
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

function ChartComponent({ selectedCompany, handleBack }) {
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
                const result = await axios.get(`/api/candles?figi_id=${selectedCompany}`);
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
                        height: chartContainerRef.current.clientHeight,
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
    }, [selectedCompany, lastPrice]);

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
            <div className="header" style={{ backgroundColor: companyColors[selectedCompany] }}>
                <h1>{companyName}</h1>
                <p>Сектор: Финансовый сектор</p>
            </div>
            <div className="price">
                <h2 className={`price-display ${priceChangeClass}`}>{lastPrice}₽</h2>
                <div className="buttons">
                    <button>Продать</button>
                    <button>Купить</button>
                </div>
            </div>
            <div className="chart-container" ref={chartContainerRef} style={{ width: '100%', height: '600px' }}></div>
            <div className="dividends">
                <p>Чтобы получить будущие дивиденды в размере 33,3₽ на одну акцию, нужно чтобы бумаги были в портфеле до конца 10.07.2024.</p>
            </div>
            <button onClick={handleBack} className="back-button">Назад в главное меню</button>
        </div>
    );
}

export default ChartComponent;
