'use client';

import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

interface ChromaGridProps {
    className?: string;
    cellSize?: number;
    gap?: number;
    colors?: string[];
    speed?: number;
}

export default function ChromaGrid({
    className,
    cellSize = 60,
    gap = 4,
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'],
    speed = 2,
}: ChromaGridProps) {
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

            const cols = Math.ceil(width / (cellSize + gap));
            const rows = Math.ceil(height / (cellSize + gap));

            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < cols; col++) {
                    const x = col * (cellSize + gap);
                    const y = row * (cellSize + gap);

                    // Create wave effect
                    const wave = Math.sin((col + row + timeRef.current * speed) * 0.3) * 0.5 + 0.5;
                    const colorIndex = Math.floor((wave * colors.length + timeRef.current * 0.1) % colors.length);

                    ctx.fillStyle = colors[colorIndex];
                    ctx.globalAlpha = 0.1 + wave * 0.15;

                    ctx.beginPath();
                    ctx.roundRect(x, y, cellSize, cellSize, 8);
                    ctx.fill();
                }
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
    }, [cellSize, gap, colors, speed, mounted]);

    if (!mounted) {
        return <div className={cn('absolute inset-0 w-full h-full bg-slate-900/50', className)} />;
    }

    return (
        <canvas
            ref={canvasRef}
            className={cn('absolute inset-0 w-full h-full pointer-events-none', className)}
        />
    );
}
