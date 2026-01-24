import React from 'react';

interface PromptInputProps {
    value: string;
    onChange: (value: string) => void;
    disabled?: boolean;
}

const PromptInput: React.FC<PromptInputProps> = ({ value, onChange, disabled = false }) => {
    return (
        <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Describe the concept you want to visualize... (e.g., 'Explain gradient descent visually')"
            maxLength={300}
            rows={4}
            disabled={disabled}
            className={`
                w-full p-4 
                bg-gray-900 
                border border-gray-600 
                rounded-lg 
                text-white 
                placeholder-gray-500
                focus:outline-none 
                focus:border-blue-500 
                focus:ring-1 
                focus:ring-blue-500
                resize-none
                transition-colors
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
        />
    );
};

export default PromptInput;