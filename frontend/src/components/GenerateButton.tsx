import React from 'react';

interface GenerateButtonProps {
    onClick: () => void;
    loading: boolean;
    disabled?: boolean;
}

const GenerateButton: React.FC<GenerateButtonProps> = ({ onClick, loading, disabled = false }) => {
    return (
        <button
            onClick={onClick}
            disabled={loading || disabled}
            className={`
                w-full py-3 px-6 
                text-white font-semibold text-lg
                rounded-lg 
                transition-all duration-200
                ${loading || disabled
                    ? 'bg-gray-600 cursor-not-allowed opacity-50'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                }
            `}
        >
            {loading ? (
                <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="none"
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                    </svg>
                    Generating...
                </span>
            ) : (
                <span className="flex items-center justify-center gap-2">
                    <span>🎬</span>
                    Generate Video
                </span>
            )}
        </button>
    );
};

export default GenerateButton;