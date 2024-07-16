import React, { useState, useEffect } from 'react';

const CompanySelector = ({ onSelect }) => {
    const [companies, setCompanies] = useState([]);

    useEffect(() => {
        fetch('/api/company_list')
            .then(response => response.json())
            .then(data => {
                const companyArray = Object.keys(data).map(name => ({
                    id: data[name],
                    name: name.charAt(0).toUpperCase() + name.slice(1)
                }));
                setCompanies(companyArray);
            })
            .catch(error => console.error('Error fetching company list:', error));
    }, []); 

    return (
        <div className="company-selector">
            <h1>Выберите компанию</h1>
            {companies.map(company => (
                <button key={company.id} onClick={() => onSelect(company.id)}>
                    {company.name}
                </button>
            ))}
        </div>
    );
};

export default CompanySelector;
