import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TopList from './TopList';
import ChartComponent from './ChartComponent';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<TopList />} />
                <Route path="/chart/:figi_id" element={<ChartComponent />} />
            </Routes>
        </Router>
    );
}

export default App;
