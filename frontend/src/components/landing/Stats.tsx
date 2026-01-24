'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import DotGrid from '../animations/DotGrid';

const STATS = [
    { value: '< 60s', label: 'Average generation time' },
    { value: '100%', label: 'Open source' },
    { value: '∞', label: 'Concepts you can visualize' },
    { value: '0', label: 'Animation skills required' },
];

export default function Stats() {
    const sectionRef = useRef<HTMLElement>(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setIsVisible(true);
                    }
                });
            },
            { threshold: 0.2 }
        );

        if (sectionRef.current) {
            observer.observe(sectionRef.current);
        }

        return () => observer.disconnect();
    }, []);

    return (
        <section
            ref={sectionRef}
            className="relative py-20 bg-slate-950 border-y border-white/5 overflow-hidden"
        >
            {/* Dot Grid Background */}
            <div className="absolute inset-0 opacity-30">
                <DotGrid
                    dotSize={1}
                    gap={24}
                    color="rgba(255, 255, 255, 0.15)"
                    hoverColor="#F24C4C"
                    waveSpeed={0.5}
                />
            </div>

            <div className="relative z-10 max-w-6xl mx-auto px-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    {STATS.map((stat, index) => (
                        <motion.div
                            key={stat.label}
                            className="text-center"
                            initial={{ opacity: 0, y: 20 }}
                            animate={isVisible ? { opacity: 1, y: 0 } : {}}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                        >
                            <div className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-nimator-red to-nimator-coral mb-2">
                                {stat.value}
                            </div>
                            <div className="text-gray-500 text-sm">
                                {stat.label}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
