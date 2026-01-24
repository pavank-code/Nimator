'use client';

import React, { useEffect, useRef, useState } from 'react';

interface VoiceNotchProps {
    isListening: boolean;
    isSpeaking: boolean;
    onToggleListen: () => void;
}

export default function VoiceNotch({ isListening, isSpeaking, onToggleListen }: VoiceNotchProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number>();
    const analyserRef = useRef<AnalyserNode | null>(null);
    const [audioLevel, setAudioLevel] = useState(0);

    // Set up audio visualization when listening
    useEffect(() => {
        if (isListening) {
            setupAudioVisualization();
        } else {
            if (analyserRef.current) {
                analyserRef.current = null;
            }
        }

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [isListening]);

    // Animate when speaking
    useEffect(() => {
        if (isSpeaking) {
            animateSpeaking();
        }
    }, [isSpeaking]);

    const setupAudioVisualization = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const audioContext = new AudioContext();
            const source = audioContext.createMediaStreamSource(stream);
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            source.connect(analyser);
            analyserRef.current = analyser;

            visualize();
        } catch (error) {
            console.error('Audio visualization error:', error);
        }
    };

    const visualize = () => {
        if (!canvasRef.current || !analyserRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const analyser = analyserRef.current;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            if (!analyserRef.current) return;

            animationRef.current = requestAnimationFrame(draw);
            analyser.getByteFrequencyData(dataArray);

            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
            setAudioLevel(average / 255);

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw waveform bars
            const barCount = 20;
            const barWidth = canvas.width / barCount - 2;
            const centerY = canvas.height / 2;

            for (let i = 0; i < barCount; i++) {
                const dataIndex = Math.floor((i / barCount) * bufferLength);
                const value = dataArray[dataIndex] / 255;
                const barHeight = Math.max(4, value * centerY * 1.5);

                // Create gradient
                const gradient = ctx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight);
                gradient.addColorStop(0, '#60a5fa');
                gradient.addColorStop(0.5, '#3b82f6');
                gradient.addColorStop(1, '#60a5fa');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.roundRect(
                    i * (barWidth + 2) + 1,
                    centerY - barHeight,
                    barWidth,
                    barHeight * 2,
                    3
                );
                ctx.fill();
            }
        };

        draw();
    };

    const animateSpeaking = () => {
        if (!canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let phase = 0;

        const draw = () => {
            if (!isSpeaking) return;

            animationRef.current = requestAnimationFrame(draw);

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const barCount = 20;
            const barWidth = canvas.width / barCount - 2;
            const centerY = canvas.height / 2;

            for (let i = 0; i < barCount; i++) {
                const value = Math.sin(phase + i * 0.3) * 0.5 + 0.5;
                const barHeight = Math.max(4, value * centerY);

                // Create gradient - purple for AI speaking
                const gradient = ctx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight);
                gradient.addColorStop(0, '#c084fc');
                gradient.addColorStop(0.5, '#a855f7');
                gradient.addColorStop(1, '#c084fc');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.roundRect(
                    i * (barWidth + 2) + 1,
                    centerY - barHeight,
                    barWidth,
                    barHeight * 2,
                    3
                );
                ctx.fill();
            }

            phase += 0.1;
        };

        draw();
    };

    const getStatusText = () => {
        if (isListening) return 'Listening...';
        if (isSpeaking) return 'Speaking...';
        return 'Tap to speak';
    };

    const getStatusColor = () => {
        if (isListening) return 'text-blue-400';
        if (isSpeaking) return 'text-purple-400';
        return 'text-gray-500';
    };

    return (
        <div className="flex justify-center py-4">
            <div
                className={`
          relative flex items-center gap-4 px-6 py-3 
          bg-gray-800/80 backdrop-blur-lg rounded-full
          border transition-all duration-300 cursor-pointer
          ${isListening ? 'border-blue-500 shadow-lg shadow-blue-500/20' : ''}
          ${isSpeaking ? 'border-purple-500 shadow-lg shadow-purple-500/20' : ''}
          ${!isListening && !isSpeaking ? 'border-gray-700 hover:border-gray-600' : ''}
        `}
                onClick={!isSpeaking ? onToggleListen : undefined}
            >
                {/* Microphone Icon */}
                <div className={`
          p-2 rounded-full transition-all
          ${isListening ? 'bg-blue-500/20' : ''}
          ${isSpeaking ? 'bg-purple-500/20' : ''}
        `}>
                    {isSpeaking ? (
                        <svg className="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                        </svg>
                    ) : (
                        <svg className={`w-5 h-5 ${isListening ? 'text-blue-400 animate-pulse' : 'text-gray-400'}`} fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                        </svg>
                    )}
                </div>

                {/* Audio Visualization Canvas */}
                <canvas
                    ref={canvasRef}
                    width={160}
                    height={40}
                    className="rounded"
                />

                {/* Status Text */}
                <span className={`text-sm font-medium ${getStatusColor()}`}>
                    {getStatusText()}
                </span>

                {/* Pulsing indicator when active */}
                {(isListening || isSpeaking) && (
                    <div className={`
            absolute -top-1 -right-1 w-3 h-3 rounded-full
            ${isListening ? 'bg-blue-500' : 'bg-purple-500'}
            animate-ping
          `} />
                )}
            </div>
        </div>
    );
}
