import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles/TopList.css';
import CurrencyRates from './CurrencyRates';
import { useNavigate } from 'react-router-dom';
import VoiceAssistant from './VoiceAssistant';
import StockPrices from './StockPrices';
import TopGrowthDecline from './TopGrowthDecline';  // Импортируем новый компонент

const TopList = () => {
    const [topVolume, setTopVolume] = useState([]);
    const [topGainers, setTopGainers] = useState([]);
    const [topLosers, setTopLosers] = useState([]);
    const [searchResults, setSearchResults] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');

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
        navigate(`/detailed-list/${type}`);
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

    const handleSearch = async (event) => {
        setSearchQuery(event.target.value);
        if (event.target.value.trim() === '') {
            setSearchResults([]);
            return;
        }

        try {
            const result = await axios.get(`/api/search?query=${event.target.value}`);
            setSearchResults(result.data);
        } catch (error) {
            console.error('Error searching companies:', error);
        }
    };

    const renderSearchResults = () => {
        return (
            <ul className="search-results">
                {searchResults.map((item, index) => (
                    <li key={index} className="list-item" onClick={() => navigate(`/chart/${item.figi_id}`)}>
                        <img src={`/company_logos/${item.figi_id}.png`} alt={`${item.company_name} logo`} className="company-logo1" />
                        <div className="company-info">
                            {item.company_name}
                        </div>
                    </li>
                ))}
            </ul>
        );
    };


    return (
        <div className="top-list">
            <CurrencyRates /> {/* Include CurrencyRates component */}
            <div className="search-section">
                <input
                    type="text"
                    placeholder="Название компании"
                    value={searchQuery}
                    onChange={handleSearch}
                />
                {searchQuery && renderSearchResults()}
            </div>
            <div className="top-sections">
                <div className="top-section">
                    <h2>Топ по обороту</h2>
                    <ul>
                        {renderListItems(topVolume.slice(0, 3))}
                    </ul>
                    <button onClick={() => handleShowAll('volume')}>
                        Смотреть все
                    </button>
                </div>
                <div className="top-section">
                    <h2>Взлеты дня</h2>
                    <ul>
                        {renderListItems(topGainers.slice(0, 3))}
                    </ul>
                    <button onClick={() => handleShowAll('gainers')}>
                        Смотреть все
                    </button>
                </div>
                <div className="top-section">
                    <h2>Падения дня</h2>
                    <ul>
                        {renderListItems(topLosers.slice(0, 3))}
                    </ul>
                    <button onClick={() => handleShowAll('losers')}>
                        Смотреть все
                    </button>
                </div>
            </div>
            <StockPrices />
            <TopGrowthDecline /> {/* Добавляем новый компонент */}
            <VoiceAssistant /> {/* Добавляем VoiceAssistant */}
        </div>
    );
};

export default TopList;
