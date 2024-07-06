import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './TopList.css';

const TopList = () => {
    const [topVolume, setTopVolume] = useState([]);
    const [topGainers, setTopGainers] = useState([]);
    const [topLosers, setTopLosers] = useState([]);
    const [showAll, setShowAll] = useState({ volume: false, gainers: false, losers: false });

    useEffect(() => {
        const fetchTopVolume = async () => {
            try {
                const result = await axios.get('/api/top_volume');
                console.log('Top Volume:', result.data);
                setTopVolume(result.data);
            } catch (error) {
                console.error('Error fetching top volume:', error);
            }
        };
        const fetchTopGainers = async () => {
            try {
                const result = await axios.get('/api/top_gainers');
                console.log('Top Gainers:', result.data);
                setTopGainers(result.data);
            } catch (error) {
                console.error('Error fetching top gainers:', error);
            }
        };
        const fetchTopLosers = async () => {
            try {
                const result = await axios.get('/api/top_losers');
                console.log('Top Losers:', result.data);
                setTopLosers(result.data);
            } catch (error) {
                console.error('Error fetching top losers:', error);
            }
        };

        fetchTopVolume();
        fetchTopGainers();
        fetchTopLosers();
    }, []);

    const handleShowAll = (type) => {
        setShowAll({ ...showAll, [type]: !showAll[type] });
    };

    const formatPercentage = (value) => {
        console.log('Formatting percentage:', value);
        return value !== undefined && value !== null ? value.toFixed(4) : '0.0000';
    };

    return (
        <div className="top-list">
            <div className="top-section">
                <h2>Топ по обороту</h2>
                <ul>
                    {(showAll.volume ? topVolume : topVolume.slice(0, 3)).map((item, index) => (
                        <li key={index}>
                            {item.company_name} - {item.total_volume} ₽
                        </li>
                    ))}
                </ul>
                <button onClick={() => handleShowAll('volume')}>
                    {showAll.volume ? 'Скрыть' : 'Смотреть все'}
                </button>
            </div>
            <div className="top-section">
                <h2>Взлеты дня</h2>
                <ul>
                    {(showAll.gainers ? topGainers : topGainers.slice(0, 3)).map((item, index) => (
                        <li key={index} style={{ color: item.percentage_change > 0 ? 'green' : 'red' }}>
                            {item.company_name} - {formatPercentage(item.percentage_change)}%
                        </li>
                    ))}
                </ul>
                <button onClick={() => handleShowAll('gainers')}>
                    {showAll.gainers ? 'Скрыть' : 'Смотреть все'}
                </button>
            </div>
            <div className="top-section">
                <h2>Падения дня</h2>
                <ul>
                    {(showAll.losers ? topLosers : topLosers.slice(0, 3)).map((item, index) => (
                        <li key={index} style={{ color: item.percentage_change < 0 ? 'red' : 'green' }}>
                            {item.company_name} - {formatPercentage(item.percentage_change)}%
                        </li>
                    ))}
                </ul>
                <button onClick={() => handleShowAll('losers')}>
                    {showAll.losers ? 'Скрыть' : 'Смотреть все'}
                </button>
            </div>
        </div>
    );
};

export default TopList;
