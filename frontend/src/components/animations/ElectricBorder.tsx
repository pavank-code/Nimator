'use client';

import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface ElectricBorderProps {
    children: React.ReactNode;
    className?: string;
    borderWidth?: number;
    borderRadius?: number;
    gradientColors?: string[];
    animationSpeed?: number;
}

export default function ElectricBorder({
    children,
    className,
    borderWidth = 2,
    borderRadius = 16,
    gradientColors = ['#667eea', '#764ba2', '#f093fb', '#667eea'],
    animationSpeed = 3,
}: ElectricBorderProps) {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div
            className={cn('relative group', className)}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Animated Border */}
            <div
                className="absolute inset-0 pointer-events-none overflow-hidden"
                style={{ borderRadius: borderRadius }}
            >
                <motion.div
                    className="absolute inset-0"
                    animate={{
                        background: [
                            `linear-gradient(0deg, ${gradientColors.join(', ')})`,
                            `linear-gradient(90deg, ${gradientColors.join(', ')})`,
                            `linear-gradient(180deg, ${gradientColors.join(', ')})`,
                            `linear-gradient(270deg, ${gradientColors.join(', ')})`,
                            `linear-gradient(360deg, ${gradientColors.join(', ')})`,
                        ],
                    }}
                    transition={{
                        duration: animationSpeed,
                        repeat: Infinity,
                        ease: 'linear',
                    }}
                    style={{
                        opacity: isHovered ? 1 : 0.5,
                        transition: 'opacity 0.3s ease',
                    }}
                />
                {/* Inner cutout */}
                <div
                    className="absolute bg-apple-offwhite"
                    style={{
                        inset: borderWidth,
                        borderRadius: borderRadius - borderWidth,
                    }}
                />
            </div>

            {/* Content */}
            <div
                className="relative z-10"
                style={{
                    padding: borderWidth,
                    borderRadius: borderRadius,
                }}
            >
                {children}
            </div>
        </div>
    );
}
