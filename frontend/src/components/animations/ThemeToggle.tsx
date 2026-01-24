'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../../context/ThemeContext';

export default function ThemeToggle() {
    const { theme, setTheme } = useTheme();

    const toggleTheme = () => {
        setTheme(theme === 'dark' ? 'light' : 'dark');
    };

    return (
        <button
            onClick={toggleTheme}
            className="relative w-14 h-7 rounded-full p-1 transition-colors duration-300
        bg-slate-700 dark:bg-slate-700 light:bg-gray-300"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
            {/* Slider */}
            <motion.div
                className="w-5 h-5 rounded-full bg-white shadow-md flex items-center justify-center"
                animate={{
                    x: theme === 'dark' ? 0 : 26,
                }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            >
                {/* Icon */}
                {theme === 'dark' ? (
                    <span className="text-xs">🌙</span>
                ) : (
                    <span className="text-xs">☀️</span>
                )}
            </motion.div>
        </button>
    );
}
