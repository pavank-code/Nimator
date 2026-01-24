'use client';

import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

interface DitherProps {
    className?: string;
    density?: number;
    speed?: number;
    colors?: string[];
}

export default function Dither({
    className,
    density = 2,
    speed = 0.5,
    colors = ['#8b5cf6', '#ec4899', '#6366f1'],
}: DitherProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number>(0);
    const timeRef = useRef(0);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!mounted) return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const resizeCanvas = () => {
            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            ctx.scale(dpr, dpr);
        };

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const animate = () => {
            if (!canvas || !ctx) return;

            const width = canvas.getBoundingClientRect().width;
            const height = canvas.getBoundingClientRect().height;

            ctx.clearRect(0, 0, width, height);

            const pixelSize = 4 / density;
            const cols = Math.ceil(width / pixelSize);
            const rows = Math.ceil(height / pixelSize);

            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < cols; col++) {
                    const x = col * pixelSize;
                    const y = row * pixelSize;

                    // Create dithering pattern with animation
                    const noise = Math.sin(col * 0.1 + timeRef.current) *
                        Math.cos(row * 0.1 + timeRef.current * 0.7);

                    if (Math.random() < 0.15 + noise * 0.1) {
                        const colorIndex = Math.floor(Math.random() * colors.length);
                        ctx.fillStyle = colors[colorIndex];
                        ctx.globalAlpha = 0.1 + Math.random() * 0.2;
                        ctx.fillRect(x, y, pixelSize, pixelSize);
                    }
                }
            }

            ctx.globalAlpha = 1;
            timeRef.current += 0.02 * speed;
            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            cancelAnimationFrame(animationRef.current);
        };
    }, [density, speed, colors, mounted]);

    if (!mounted) {
        return <div className={cn('absolute inset-0 w-full h-full', className)} />;
    }

    return (
        <canvas
            ref={canvasRef}
            className={cn('absolute inset-0 w-full h-full pointer-events-none', className)}
        />
    );
}
