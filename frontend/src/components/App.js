import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TopList from './TopList';
import ChartComponent from './ChartComponent';
import DetailedList from './DetailedList';
import VoiceAssistant from './VoiceAssistant';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<TopList />} />
                <Route path="/chart/:figi_id" element={<ChartComponent />} />
                <Route path="/detailed-list/:type" element={<DetailedList />} /> 
                <Route path="/voice-assistant" element={<VoiceAssistant />} /> 
            </Routes>
        </Router>
    );
};

export default App;
