'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { cn } from '../../lib/utils';

interface DockItem {
    label: string;
    href: string;
    icon?: React.ReactNode;
    onClick?: () => void;
}

interface DockProps {
    items: DockItem[];
    className?: string;
    magnification?: number;
    baseSize?: number;
}

export default function Dock({
    items,
    className,
    magnification = 1.4,
    baseSize = 48,
}: DockProps) {
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const getScale = (index: number) => {
        if (hoveredIndex === null) return 1;

        const distance = Math.abs(index - hoveredIndex);
        if (distance === 0) return magnification;
        if (distance === 1) return 1 + (magnification - 1) * 0.5;
        if (distance === 2) return 1 + (magnification - 1) * 0.2;
        return 1;
    };

    return (
        <motion.div
            ref={containerRef}
            className={cn(
                'flex items-end gap-2 px-4 py-2 rounded-2xl',
                'bg-black/50 backdrop-blur-xl border border-white/10',
                'shadow-lg shadow-black/20',
                className
            )}
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        >
            {items.map((item, index) => (
                <motion.div
                    key={item.label}
                    className="relative"
                    onMouseEnter={() => setHoveredIndex(index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                    animate={{ scale: getScale(index) }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    style={{ originY: 1 }}
                >
                    {/* Tooltip */}
                    <AnimatePresence>
                        {hoveredIndex === index && (
                            <motion.div
                                initial={{ opacity: 0, y: 10, scale: 0.8 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: 5, scale: 0.9 }}
                                className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 
                  bg-white text-black text-xs font-medium rounded-lg whitespace-nowrap
                  shadow-lg"
                            >
                                {item.label}
                                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 
                  border-4 border-transparent border-t-white" />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Dock Item */}
                    {item.onClick ? (
                        <button
                            onClick={item.onClick}
                            className="flex items-center justify-center rounded-xl bg-gradient-to-b 
                from-gray-800 to-gray-900 shadow-md hover:shadow-lg transition-shadow
                border border-white/10"
                            style={{ width: baseSize, height: baseSize }}
                        >
                            {item.icon || (
                                <span className="text-lg font-semibold text-gray-300">
                                    {item.label.charAt(0)}
                                </span>
                            )}
                        </button>
                    ) : (
                        <Link
                            href={item.href}
                            className="flex items-center justify-center rounded-xl bg-gradient-to-b 
                from-gray-800 to-gray-900 shadow-md hover:shadow-lg transition-shadow
                border border-white/10"
                            style={{ width: baseSize, height: baseSize }}
                        >
                            {item.icon || (
                                <span className="text-lg font-semibold text-gray-300">
                                    {item.label.charAt(0)}
                                </span>
                            )}
                        </Link>
                    )}
                </motion.div>
            ))}
        </motion.div>
    );
}
