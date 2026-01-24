'use client';

import React, { useEffect, useRef, useState } from 'react';

interface AuroraProps {
    colorStops?: string[];
    amplitude?: number;
    speed?: number;
    blend?: number;
    className?: string;
}

export default function Aurora({
    colorStops = ['#3A29FF', '#FF94B4', '#FF3232'],
    amplitude = 1.0,
    speed = 1.0,
    blend = 0.5,
    className = '',
}: AuroraProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number | null>(null);
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
            canvas.width = canvas.offsetWidth * window.devicePixelRatio;
            canvas.height = canvas.offsetHeight * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        };

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let time = 0;

        const animate = () => {
            time += 0.005 * speed;

            const width = canvas.offsetWidth;
            const height = canvas.offsetHeight;

            ctx.clearRect(0, 0, width, height);

            // Create multiple wave layers
            for (let layer = 0; layer < 3; layer++) {
                const layerOffset = layer * 0.3;
                const layerAmplitude = amplitude * (1 - layer * 0.2);

                ctx.beginPath();
                ctx.moveTo(0, height);

                for (let x = 0; x <= width; x += 5) {
                    const normalizedX = x / width;
                    const wave1 = Math.sin(normalizedX * 4 + time + layerOffset) * 50 * layerAmplitude;
                    const wave2 = Math.sin(normalizedX * 2 + time * 0.7 + layerOffset) * 30 * layerAmplitude;
                    const wave3 = Math.sin(normalizedX * 6 + time * 1.3 + layerOffset) * 20 * layerAmplitude;

                    const y = height * 0.5 + wave1 + wave2 + wave3;
                    ctx.lineTo(x, y);
                }

                ctx.lineTo(width, height);
                ctx.closePath();

                // Create gradient for this layer
                const gradient = ctx.createLinearGradient(0, 0, width, height);
                const colorIndex = layer % colorStops.length;
                const nextColorIndex = (layer + 1) % colorStops.length;

                gradient.addColorStop(0, colorStops[colorIndex] + Math.round(blend * 255 * 0.6).toString(16).padStart(2, '0'));
                gradient.addColorStop(0.5, colorStops[nextColorIndex] + Math.round(blend * 255 * 0.4).toString(16).padStart(2, '0'));
                gradient.addColorStop(1, colorStops[(layer + 2) % colorStops.length] + Math.round(blend * 255 * 0.3).toString(16).padStart(2, '0'));

                ctx.fillStyle = gradient;
                ctx.fill();
            }

            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [colorStops, amplitude, speed, blend, mounted]);

    if (!mounted) {
        return (
            <div
                className={`absolute inset-0 bg-gradient-to-br from-purple-900/30 to-pink-900/30 ${className}`}
            />
        );
    }

    return (
        <canvas
            ref={canvasRef}
            className={`absolute inset-0 w-full h-full ${className}`}
            style={{ mixBlendMode: 'screen' }}
        />
    );
}
