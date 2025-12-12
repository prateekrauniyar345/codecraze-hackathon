import React from 'react';

const MultiSelectChipFilter = ({ label, options, selected, onChange }) => {
    const handleSelect = (option) => {
        const newSelected = selected.includes(option)
            ? selected.filter(item => item !== option)
            : [...selected, option];
        onChange(newSelected);
    };

    return (
        <div className="mb-4">
            <h4 className="font-semibold mb-2">{label}</h4>
            <div className="flex flex-wrap gap-2">
                {options.map(option => (
                    <button
                        key={option.value}
                        onClick={() => handleSelect(option.value)}
                        className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                            selected.includes(option.value)
                                ? 'bg-primary-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default MultiSelectChipFilter;
