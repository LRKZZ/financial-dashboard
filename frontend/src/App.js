import React, { useState } from 'react';
import './App.css';
import CompanySelector from './CompanySelector';
import TopList from './TopList';
import ChartComponent from './ChartComponent';

function App() {
    const [selectedCompany, setSelectedCompany] = useState(null);

    const handleCompanySelect = (companyId) => {
        setSelectedCompany(companyId);
    };

    const handleBack = () => {
        setSelectedCompany(null);
    };

    return (
        <div className="app">
            {selectedCompany === null ? (
                <>
                    <TopList />
                    <CompanySelector onSelect={handleCompanySelect} />
                </>
            ) : (
                <ChartComponent selectedCompany={selectedCompany} handleBack={handleBack} />
            )}
        </div>
    );
}

export default App;
