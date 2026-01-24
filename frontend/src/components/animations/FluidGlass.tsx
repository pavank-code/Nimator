'use client';

import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface FluidGlassProps {
    children: React.ReactNode;
    className?: string;
    intensity?: number;
    blur?: number;
    tint?: string;
}

export default function FluidGlass({
    children,
    className,
    intensity = 0.3,
    blur = 12,
    tint = 'rgba(255, 255, 255, 0.1)',
}: FluidGlassProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [mousePosition, setMousePosition] = useState({ x: 0.5, y: 0.5 });

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;

        setMousePosition({ x, y });
    };

    const handleMouseLeave = () => {
        setMousePosition({ x: 0.5, y: 0.5 });
    };

    return (
        <motion.div
            ref={containerRef}
            className={cn('relative overflow-hidden', className)}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{
                background: `
          radial-gradient(
            circle at ${mousePosition.x * 100}% ${mousePosition.y * 100}%, 
            rgba(255, 255, 255, ${intensity * 0.6}) 0%, 
            ${tint} 50%, 
            transparent 100%
          )
        `,
                backdropFilter: `blur(${blur}px)`,
                WebkitBackdropFilter: `blur(${blur}px)`,
            }}
        >
            {/* Refraction effect layer */}
            <motion.div
                className="absolute inset-0 pointer-events-none"
                animate={{
                    background: `
            radial-gradient(
              ellipse at ${mousePosition.x * 100}% ${mousePosition.y * 100}%, 
              rgba(255, 255, 255, ${intensity}) 0%, 
              transparent 50%
            )
          `,
                }}
                transition={{ type: 'spring', stiffness: 150, damping: 15 }}
            />

            {/* Content */}
            <div className="relative z-10">
                {children}
            </div>
        </motion.div>
    );
}
