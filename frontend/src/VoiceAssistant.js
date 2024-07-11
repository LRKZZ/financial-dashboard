import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './VoiceAssistant.css';

const companyList = {
    'лукойл': 1,
    'роснефть': 2,
    'втб': 3,
    'газпром': 4,
    'мтс': 5,
    'сбербанк': 6,
    'новатэк': 7,
    'интер рао': 8,
    'сургутнефтегаз': 9,
    'афк система': 10
};

const VoiceAssistant = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [pendingCompany, setPendingCompany] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Ваш браузер не поддерживает Web Speech API');
            return;
        }

        const recognition = new window.webkitSpeechRecognition();
        recognition.lang = 'ru-RU';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript.toLowerCase();
            setTranscript(speechResult);
            setChatHistory(prev => [...prev, { text: speechResult, user: true }]);

            for (const company in companyList) {
                if (speechResult.includes(company)) {
                    setPendingCompany(company);
                    const response = `Вы хотите открыть котировки компании ${company}?`;
                    setTranscript(response);
                    setChatHistory(prev => [...prev, { text: response, user: false }]);
                    return;
                }
            }

            if (pendingCompany) {
                if (speechResult.includes('да')) {
                    navigate(`/chart/${companyList[pendingCompany]}`);
                    setPendingCompany(null);
                } else if (speechResult.includes('нет')) {
                    setPendingCompany(null);
                }
            }
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        if (isListening) {
            recognition.start();
        } else {
            recognition.stop();
        }

        return () => {
            recognition.stop();
        };
    }, [isListening, pendingCompany, navigate]);

    const toggleListening = () => {
        setIsListening(!isListening);
    };

    return (
        <div className="voice-assistant">
            <div className="chat-window">
                {chatHistory.map((entry, index) => (
                    <div key={index} className={`chat-bubble ${entry.user ? 'user' : 'assistant'}`}>
                        {entry.text}
                    </div>
                ))}
            </div>
            <button 
                onClick={toggleListening} 
                className={`mic-button ${isListening ? 'listening' : ''}`}
            >
                <img src="/company_logos/micro.png" alt="Микрофон" className="mic-icon" />
            </button>
        </div>
    );
};

export default VoiceAssistant;
