import React from 'react';

const LoadingSpinner: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center">
            <div className="relative">
                {/* Outer ring */}
                <div className="w-16 h-16 border-4 border-gray-700 rounded-full"></div>
                {/* Spinning gradient ring */}
                <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-500 border-r-purple-500 rounded-full animate-spin"></div>
                {/* Inner pulse */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse opacity-50"></div>
                </div>
            </div>
        </div>
    );
};

export default LoadingSpinner;