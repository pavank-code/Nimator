'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { cn } from '../../lib/utils';

interface CardNavItem {
    id: string;
    title: string;
    description: string;
    href: string;
    icon?: React.ReactNode;
    gradient?: string;
}

interface CardNavProps {
    items: CardNavItem[];
    className?: string;
}

export default function CardNav({ items, className }: CardNavProps) {
    const [hoveredId, setHoveredId] = useState<string | null>(null);

    return (
        <nav className={cn('grid gap-4', className)}>
            {items.map((item) => (
                <Link
                    key={item.id}
                    href={item.href}
                    className="relative block group"
                    onMouseEnter={() => setHoveredId(item.id)}
                    onMouseLeave={() => setHoveredId(null)}
                >
                    <AnimatePresence>
                        {hoveredId === item.id && (
                            <motion.div
                                layoutId="card-nav-highlight"
                                className="absolute inset-0 rounded-2xl"
                                style={{
                                    background: item.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                }}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                            />
                        )}
                    </AnimatePresence>

                    <motion.div
                        className={cn(
                            'relative z-10 p-6 rounded-2xl border transition-colors duration-200',
                            hoveredId === item.id
                                ? 'border-transparent bg-white/10'
                                : 'border-gray-200 bg-white/80 backdrop-blur-sm'
                        )}
                        animate={{
                            y: hoveredId === item.id ? -2 : 0,
                        }}
                        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                    >
                        <div className="flex items-start gap-4">
                            {item.icon && (
                                <motion.div
                                    className={cn(
                                        'flex-shrink-0 p-3 rounded-xl transition-colors',
                                        hoveredId === item.id
                                            ? 'bg-white/20 text-white'
                                            : 'bg-gray-100 text-gray-600'
                                    )}
                                    animate={{
                                        scale: hoveredId === item.id ? 1.1 : 1,
                                        rotate: hoveredId === item.id ? 5 : 0,
                                    }}
                                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                                >
                                    {item.icon}
                                </motion.div>
                            )}

                            <div className="flex-1 min-w-0">
                                <h3
                                    className={cn(
                                        'font-semibold text-lg mb-1 transition-colors',
                                        hoveredId === item.id ? 'text-white' : 'text-gray-900'
                                    )}
                                >
                                    {item.title}
                                </h3>
                                <p
                                    className={cn(
                                        'text-sm leading-relaxed transition-colors',
                                        hoveredId === item.id ? 'text-white/80' : 'text-gray-500'
                                    )}
                                >
                                    {item.description}
                                </p>
                            </div>

                            <motion.div
                                className={cn(
                                    'flex-shrink-0 transition-colors',
                                    hoveredId === item.id ? 'text-white' : 'text-gray-400'
                                )}
                                animate={{
                                    x: hoveredId === item.id ? 4 : 0,
                                }}
                                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                            >
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </motion.div>
                        </div>
                    </motion.div>
                </Link>
            ))}
        </nav>
    );
}
