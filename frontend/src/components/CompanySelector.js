import React from 'react';

const companies = [
    { id: 1, name: 'ЛУКОЙЛ' },
    { id: 2, name: 'Роснефть' },
    { id: 3, name: 'ВТБ' },
    { id: 4, name: 'Газпром' },
    { id: 5, name: 'МТС' },
    { id: 6, name: 'Сбербанк' },
    { id: 7, name: 'Новатэк' },
    { id: 8, name: 'Интер РАО' },
    { id: 9, name: 'Сургутнефтегаз' },
    { id: 10, name: 'АФК Система' }
];

const CompanySelector = ({ onSelect }) => {
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
