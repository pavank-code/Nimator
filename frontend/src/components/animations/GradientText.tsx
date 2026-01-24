'use client';

import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

interface GradientTextProps {
    text: string;
    className?: string;
    colors?: string[];
    animationSpeed?: number;
    as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
}

export default function GradientText({
    text,
    className,
    colors = ['#8b5cf6', '#ec4899', '#6366f1', '#a855f7'],
    animationSpeed = 3,
    as = 'span',
}: GradientTextProps) {
    const [mounted, setMounted] = useState(false);
    const [gradientPosition, setGradientPosition] = useState(0);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!mounted) return;

        const interval = setInterval(() => {
            setGradientPosition((prev) => (prev + 1) % 200);
        }, 50 / animationSpeed);

        return () => clearInterval(interval);
    }, [animationSpeed, mounted]);

    const Component = as;

    const gradientStyle = {
        background: `linear-gradient(90deg, ${colors.join(', ')}, ${colors[0]})`,
        backgroundSize: '200% 100%',
        backgroundPosition: `${gradientPosition}% 50%`,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
    };

    if (!mounted) {
        return (
            <Component className={cn('inline-block', className)} style={gradientStyle}>
                {text}
            </Component>
        );
    }

    return (
        <Component className={cn('inline-block', className)} style={gradientStyle}>
            {text}
        </Component>
    );
}
