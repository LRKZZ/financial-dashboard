import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { createChart } from 'lightweight-charts';
import '../styles/ChartComponent.css';

const companyColors = {
    1: 'linear-gradient(to right, #ff0000, #ff7373)', // ЛУКОЙЛ - красный градиент
    2: 'linear-gradient(to right, #ffc107, #ffecb3)', // Роснефть - темновато-желтый градиент
    3: 'linear-gradient(to right, #2196f3, #64b5f6)', // ВТБ - синий градиент
    4: 'linear-gradient(to right, #2196f3, #64b5f6)', // Газпром - синий градиент
    5: 'linear-gradient(to right, #ff0000, #ff7373)', // МТС - красный градиент
    6: 'linear-gradient(to right, #4caf50, #81c784)', // Сбербанк - зеленый градиент
    7: 'linear-gradient(to right, #e0e0e0, #f5f5f5)', // Новатэк - бело-серый градиент
    8: 'linear-gradient(to right, #9e9e9e, #bdbdbd)', // Интер РАО - сероватый градиент
    9: 'linear-gradient(to right, #9e9e9e, #bdbdbd)', // Сургутнефтегаз - сероватый градиент
    10: 'linear-gradient(to right, #3f51b5, #7986cb)' // АФК Система - синеватый градиент
};

const timeFrames = {
    '1m': 'Минутный',
    '5m': 'Пятиминутный',
    '10m': '10-минутный',
    '1h': 'Часовой'
};

function ChartComponent() {
    const { figi_id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState([]);
    const [companyName, setCompanyName] = useState('');
    const [lastPrice, setLastPrice] = useState(null);
    const [priceChangeClass, setPriceChangeClass] = useState('');
    const [indicators, setIndicators] = useState({});
    const [timeFrame, setTimeFrame] = useState('1m');
    const [chartType, setChartType] = useState('candlestick'); // Тип графика: 'candlestick' или 'line'
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const seriesRef = useRef();

    const fetchData = async (frame) => {
        try {
            const result = await axios.get(`/api/candles?figi_id=${figi_id}&time_frame=${frame}`);
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
                seriesRef.current = chartRef.current.addCandlestickSeries();

                seriesRef.current.setData(result.data.candles.map(item => ({
                    time: item.time,
                    open: item.open,
                    high: item.high,
                    low: item.low,
                    close: item.close
                })));
            } else {
                seriesRef.current.setData(result.data.candles.map(item => ({
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

    const switchSeries = (type) => {
        if (seriesRef.current) {
            chartRef.current.removeSeries(seriesRef.current);
        }
        if (type === 'candlestick') {
            seriesRef.current = chartRef.current.addCandlestickSeries();
            seriesRef.current.setData(data.map(item => ({
                time: item.time,
                open: item.open,
                high: item.high,
                low: item.low,
                close: item.close
            })));
        } else if (type === 'line') {
            seriesRef.current = chartRef.current.addLineSeries();
            seriesRef.current.setData(data.map(item => ({
                time: item.time,
                value: item.close
            })));
        }
    };

    useEffect(() => {
        fetchData(timeFrame);

        const intervalId = setInterval(() => fetchData(timeFrame), 20000); // Fetch data every minute

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, [figi_id, timeFrame]);

    useEffect(() => {
        if (priceChangeClass) {
            const timeoutId = setTimeout(() => {
                setPriceChangeClass('');
            }, 1000); // Remove animation class after 1 second
            return () => clearTimeout(timeoutId);
        }
    }, [priceChangeClass]);

    useEffect(() => {
        if (chartRef.current) {
            switchSeries(chartType);
        }
    }, [chartType, data]);

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
                <button onClick={() => navigate('/detailed-list/volume')}>Топ по обороту</button>
                <button onClick={() => navigate('/detailed-list/gainers')}>Взлеты дня</button>
                <button onClick={() => navigate('/detailed-list/losers')}>Падения дня</button>
                <button onClick={() => navigate('/')}>Главное меню</button>
            </div>
            <div className="company-header" style={{ background: companyColors[figi_id] }}>
                <div className="company-info">
                    <h1 className="company-name">{companyName}</h1>
                    <p className="company-sector">Сектор: Финансовый сектор</p>
                </div>
                <img src={`/company_logos/${figi_id}.png`} alt={`${companyName} logo`} className="company-logo" />
            </div>
            <div className="price-section">
                <h2 className={`price-display ${priceChangeClass}`}>{lastPrice}₽</h2>
            </div>
            <div className="chart-container" ref={chartContainerRef}></div>
            <div className="timeframe-buttons">
                {Object.keys(timeFrames).map((frame) => (
                    <button
                        key={frame}
                        className={`timeframe-button ${frame === timeFrame ? 'active' : ''}`}
                        onClick={() => setTimeFrame(frame)}
                    >
                        {timeFrames[frame]}
                    </button>
                ))}
            </div>
            <div className="chart-type-buttons">
                <button
                    className={`chart-type-button ${chartType === 'candlestick' ? 'active' : ''}`}
                    onClick={() => setChartType('candlestick')}
                >
                    Свечи
                </button>
                <button
                    className={`chart-type-button ${chartType === 'line' ? 'active' : ''}`}
                    onClick={() => setChartType('line')}
                >
                    Линия
                </button>
            </div>
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
                                <td className={value > 0 ? 'positive' : 'negative'}>
                                    {value > 0 ? 'Покупать' : 'Продавать'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ChartComponent;
