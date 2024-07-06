import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TopList from './TopList';
import ChartComponent from './ChartComponent';
import './App.css';

function App() {
    return (
        <Router>
            <div className="app">
                <Routes>
                    <Route path="/" element={<TopList />} />
                    <Route path="/company/:figi_id" element={<ChartComponent />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
