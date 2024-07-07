import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './TopList.css';
import { useNavigate } from 'react-router-dom';

const TopList = () => {
    const [topVolume, setTopVolume] = useState([]);
    const [topGainers, setTopGainers] = useState([]);
    const [topLosers, setTopLosers] = useState([]);
    const [showAll, setShowAll] = useState({ volume: false, gainers: false, losers: false });

    const navigate = useNavigate();

    useEffect(() => {
        const fetchTopVolume = async () => {
            try {
                const result = await axios.get('/api/top_volume');
                setTopVolume(result.data);
            } catch (error) {
                console.error('Error fetching top volume:', error);
            }
        };
        const fetchTopGainers = async () => {
            try {
                const result = await axios.get('/api/top_gainers');
                setTopGainers(result.data);
            } catch (error) {
                console.error('Error fetching top gainers:', error);
            }
        };
        const fetchTopLosers = async () => {
            try {
                const result = await axios.get('/api/top_losers');
                setTopLosers(result.data);
            } catch (error) {
                console.error('Error fetching top losers:', error);
            }
        };

        fetchTopVolume();
        fetchTopGainers();
        fetchTopLosers();

        const intervalId = setInterval(() => {
            fetchTopVolume();
            fetchTopGainers();
            fetchTopLosers();
        }, 60000);

        return () => clearInterval(intervalId);
    }, []);

    const handleShowAll = (type) => {
        setShowAll({ ...showAll, [type]: !showAll[type] });
    };

    const formatPercentage = (value) => {
        return value !== undefined && value !== null ? value.toFixed(4) : '0.0000';
    };

    const renderListItems = (items) => {
        return items.map((item, index) => (
            <li key={index} className="list-item" onClick={() => navigate(`/chart/${item.figi_id}`)}>
                <img src={`/company_logos/${item.figi_id}.png`} alt={`${item.company_name} logo`} className="company-logo1" />
                <div className="company-info">
                    {item.company_name}
                    <div className={`percent-change ${item.percentage_change >= 0 ? 'positive' : 'negative'}`}>
                        {formatPercentage(item.percentage_change)}%
                    </div>
                </div>
            </li>
        ));
    };

    return (
        <div className="top-list">
            <div className="top-section">
                <h2>Топ по обороту</h2>
                <ul>
                    {renderListItems(showAll.volume ? topVolume : topVolume.slice(0, 3))}
                </ul>
                <button onClick={() => handleShowAll('volume')}>
                    {showAll.volume ? 'Скрыть' : 'Смотреть все'}
                </button>
            </div>
            <div className="top-section">
                <h2>Взлеты дня</h2>
                <ul>
                    {renderListItems(showAll.gainers ? topGainers : topGainers.slice(0, 3))}
                </ul>
                <button onClick={() => handleShowAll('gainers')}>
                    {showAll.gainers ? 'Скрыть' : 'Смотреть все'}
                </button>
            </div>
            <div className="top-section">
                <h2>Падения дня</h2>
                <ul>
                    {renderListItems(showAll.losers ? topLosers : topLosers.slice(0, 3))}
                </ul>
                <button onClick={() => handleShowAll('losers')}>
                    {showAll.losers ? 'Скрыть' : 'Смотреть все'}
                </button>
            </div>
        </div>
    );
};


export default TopList;
