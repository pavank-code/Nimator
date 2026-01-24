'use client';

import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

interface ColourBendsProps {
    className?: string;
    colors?: string[];
    speed?: number;
    opacity?: number;
}

export default function ColourBends({
    className,
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'],
    speed = 1,
    opacity = 0.6,
}: ColourBendsProps) {
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

            // Draw flowing color bands
            const numBands = colors.length;

            for (let i = 0; i < numBands; i++) {
                ctx.beginPath();
                ctx.moveTo(0, height);

                const baseY = (height / numBands) * i;
                const phase = timeRef.current * speed + i * 0.5;

                for (let x = 0; x <= width; x += 10) {
                    const y = baseY +
                        Math.sin((x * 0.005 + phase) * 2) * height * 0.15 +
                        Math.cos((x * 0.003 + phase * 0.7)) * height * 0.1;
                    ctx.lineTo(x, y);
                }

                ctx.lineTo(width, height);
                ctx.closePath();

                const gradient = ctx.createLinearGradient(0, baseY - 100, 0, baseY + 200);
                gradient.addColorStop(0, 'transparent');
                gradient.addColorStop(0.5, colors[i]);
                gradient.addColorStop(1, 'transparent');

                ctx.fillStyle = gradient;
                ctx.globalAlpha = opacity / numBands;
                ctx.fill();
            }

            ctx.globalAlpha = 1;
            timeRef.current += 0.016;
            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            cancelAnimationFrame(animationRef.current);
        };
    }, [colors, speed, opacity, mounted]);

    if (!mounted) {
        return <div className={cn('absolute inset-0 w-full h-full bg-gradient-to-br from-purple-900/20 to-pink-900/20', className)} />;
    }

    return (
        <canvas
            ref={canvasRef}
            className={cn('absolute inset-0 w-full h-full pointer-events-none', className)}
            style={{ mixBlendMode: 'multiply' }}
        />
    );
}
