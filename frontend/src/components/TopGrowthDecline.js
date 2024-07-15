import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import '../styles/TopList.css';

const TopGrowthDecline = () => {
    const [topGrowth, setTopGrowth] = useState([]);
    const [topDecline, setTopDecline] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTopGrowth = async () => {
            try {
                const result = await axios.get('/api/top_growth');
                setTopGrowth(result.data);
            } catch (error) {
                console.error('Error fetching top growth:', error);
            }
        };
        const fetchTopDecline = async () => {
            try {
                const result = await axios.get('/api/top_decline');
                setTopDecline(result.data);
            } catch (error) {
                console.error('Error fetching top decline:', error);
            }
        };

        fetchTopGrowth();
        fetchTopDecline();

        const intervalId = setInterval(() => {
            fetchTopGrowth();
            fetchTopDecline();
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

    return (
        <div className="top-growth-decline">
            <div className="top-sections">
                <div className="top-section">
                    <h2>Исторический рост</h2>
                    <ul>
                        {renderListItems(topGrowth.slice(0, 3))}
                    </ul>
                    <button onClick={() => handleShowAll('growth')}>
                        Смотреть все
                    </button>
                </div>
                <div className="top-section">
                    <h2>Историческое падение</h2>
                    <ul>
                        {renderListItems(topDecline.slice(0, 3))}
                    </ul>
                    <button onClick={() => handleShowAll('decline')}>
                        Смотреть все
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TopGrowthDecline;
