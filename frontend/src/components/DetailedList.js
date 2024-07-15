import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/DetailedList.css';

const DetailedList = () => {
    const { type } = useParams();
    const [items, setItems] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await axios.get(`/api/top_${type}`);
                setItems(result.data);
            } catch (error) {
                console.error(`Error fetching top ${type}:`, error);
            }
        };
        fetchData();
    }, [type]);

    const formatPercentage = (value) => {
        return value !== undefined && value !== null ? value.toFixed(4) : '0.0000';
    };

    return (
        <div className="detailed-list">
            <button className="back-button" onClick={() => navigate(-1)}>Назад</button>
            <h2>{type === 'volume' ? 'Топ по обороту' : type === 'gainers' ? 'Взлеты дня' : 'Падения дня'}</h2>
            <ul>
                {items.map((item, index) => (
                    <li key={index} className="list-item" onClick={() => navigate(`/chart/${item.figi_id}`)}>
                        <img src={`/company_logos/${item.figi_id}.png`} alt={`${item.company_name} logo`} className="company-logo2" />
                        <div className="company-info">
                            {item.company_name}
                            <div className={`percent-change ${item.percentage_change >= 0 ? 'positive' : 'negative'}`}>
                                {formatPercentage(item.percentage_change)}%
                            </div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DetailedList;
