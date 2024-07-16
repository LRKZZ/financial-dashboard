import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { createChart } from 'lightweight-charts';
import '../styles/ChartComponent.css';

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
    const [chartType, setChartType] = useState('candlestick');
    const [companyColor, setCompanyColor] = useState('linear-gradient(to right, #ffffff, #ffffff)');
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const seriesRef = useRef();

    const fetchCompanyDetails = async (figi_id) => {
        try {
            const response = await axios.get('/api/company_list');
            const companyList = response.data;
            for (const company in companyList) {
                if (companyList[company].id === parseInt(figi_id)) {
                    setCompanyColor(companyList[company].color);
                    setCompanyName(company.charAt(0).toUpperCase() + company.slice(1));
                    break;
                }
            }
        } catch (error) {
            console.error('Error fetching company details:', error);
        }
    };

    const fetchData = async (frame) => {
        try {
            const result = await axios.get(`/api/candles?figi_id=${figi_id}&time_frame=${frame}`);
            setData(result.data.candles);
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
        fetchCompanyDetails(figi_id);
        fetchData(timeFrame);

        const intervalId = setInterval(() => fetchData(timeFrame), 20000);

        return () => clearInterval(intervalId);
    }, [figi_id, timeFrame]);

    useEffect(() => {
        if (priceChangeClass) {
            const timeoutId = setTimeout(() => {
                setPriceChangeClass('');
            }, 1000);
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
            <div className="company-header" style={{ background: companyColor }}>
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
