'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface DarkVeilProps {
    children: React.ReactNode;
    className?: string;
    veilColor?: string;
    intensity?: number;
    radius?: number;
}

export default function DarkVeil({
    children,
    className,
    veilColor = 'rgba(0, 0, 0, 0.85)',
    intensity = 200,
    radius = 150,
}: DarkVeilProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [mousePosition, setMousePosition] = useState({ x: -1000, y: -1000 });
    const [isHovering, setIsHovering] = useState(false);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        setMousePosition({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        });
    };

    return (
        <div
            ref={containerRef}
            className={cn('relative overflow-hidden', className)}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => {
                setIsHovering(false);
                setMousePosition({ x: -1000, y: -1000 });
            }}
        >
            {/* Content (revealed through veil) */}
            <div className="relative z-10">
                {children}
            </div>

            {/* Dark Veil Overlay */}
            <motion.div
                className="absolute inset-0 z-20 pointer-events-none"
                animate={{
                    background: isHovering
                        ? `radial-gradient(circle ${radius}px at ${mousePosition.x}px ${mousePosition.y}px, transparent 0%, ${veilColor} 100%)`
                        : veilColor,
                }}
                transition={{ type: 'tween', duration: 0.1 }}
            />

            {/* Glow effect at cursor */}
            {isHovering && (
                <motion.div
                    className="absolute z-30 pointer-events-none rounded-full"
                    animate={{
                        x: mousePosition.x - radius / 2,
                        y: mousePosition.y - radius / 2,
                    }}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    style={{
                        width: radius,
                        height: radius,
                        background: `radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)`,
                    }}
                />
            )}
        </div>
    );
}
