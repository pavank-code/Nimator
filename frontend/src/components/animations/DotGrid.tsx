'use client';

import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

interface DotGridProps {
    className?: string;
    dotSize?: number;
    gap?: number;
    color?: string;
    hoverColor?: string;
    waveSpeed?: number;
}

export default function DotGrid({
    className,
    dotSize = 3,
    gap = 20,
    color = 'rgba(139, 92, 246, 0.3)',
    hoverColor = 'rgba(236, 72, 153, 0.8)',
    waveSpeed = 1,
}: DotGridProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number>(0);
    const timeRef = useRef(0);
    const mouseRef = useRef({ x: -1000, y: -1000 });
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

        const handleMouseMove = (e: MouseEvent) => {
            const rect = canvas.getBoundingClientRect();
            mouseRef.current = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top,
            };
        };

        const handleMouseLeave = () => {
            mouseRef.current = { x: -1000, y: -1000 };
        };

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseleave', handleMouseLeave);

        const animate = () => {
            if (!canvas || !ctx) return;

            const width = canvas.getBoundingClientRect().width;
            const height = canvas.getBoundingClientRect().height;

            ctx.clearRect(0, 0, width, height);

            const cols = Math.ceil(width / gap);
            const rows = Math.ceil(height / gap);

            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < cols; col++) {
                    const x = col * gap + gap / 2;
                    const y = row * gap + gap / 2;

                    // Distance from mouse
                    const dx = mouseRef.current.x - x;
                    const dy = mouseRef.current.y - y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const maxDistance = 100;

                    // Wave animation
                    const wave = Math.sin((col + row + timeRef.current * waveSpeed) * 0.3) * 0.5 + 0.5;

                    // Size based on distance and wave
                    let size = dotSize;
                    let dotColor = color;

                    if (distance < maxDistance) {
                        const proximity = 1 - distance / maxDistance;
                        size = dotSize + proximity * dotSize * 2;
                        dotColor = hoverColor;
                    } else {
                        size = dotSize + wave * dotSize * 0.5;
                    }

                    ctx.beginPath();
                    ctx.arc(x, y, size, 0, Math.PI * 2);
                    ctx.fillStyle = dotColor;
                    ctx.fill();
                }
            }

            timeRef.current += 0.016;
            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            canvas.removeEventListener('mousemove', handleMouseMove);
            canvas.removeEventListener('mouseleave', handleMouseLeave);
            cancelAnimationFrame(animationRef.current);
        };
    }, [dotSize, gap, color, hoverColor, waveSpeed, mounted]);

    if (!mounted) {
        return <div className={cn('absolute inset-0 w-full h-full', className)} />;
    }

    return (
        <canvas
            ref={canvasRef}
            className={cn('absolute inset-0 w-full h-full', className)}
        />
    );
}
