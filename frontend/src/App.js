import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
    const [chartData, setChartData] = useState([]);
    const [showAnimation, setShowAnimation] = useState(true);

    useEffect(() => {
        axios.get('/api/data')
            .then(response => {
                const formattedData = response.data.map(item => ({
                    time_of_candle: new Date(item.time_of_candle).toLocaleString(),
                    open_price: item.open_price,
                }));
                setChartData(formattedData);
            })
            .catch(error => console.error('Error fetching data:', error));

        const timer = setTimeout(() => {
            setShowAnimation(false);
        }, 3000);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="App">
            {showAnimation ? (
                <header className="App-header">
                    <motion.div
                        initial={{ opacity: 0, y: -50 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1 }}
                    >
                        <h1>Investing & Finance</h1>
                    </motion.div>
                </header>
            ) : (
                <div className="chart-container">
                    <h2>Stock Prices</h2>
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart
                            data={chartData}
                            margin={{
                                top: 5, right: 30, left: 20, bottom: 5,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time_of_candle" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="open_price" stroke="#8884d8" activeDot={{ r: 8 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
}

export default App;
