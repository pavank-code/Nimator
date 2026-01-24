'use client';

import React, { useState, useEffect } from 'react';

interface VideoPlayerModalProps {
    isOpen: boolean;
    onClose: () => void;
    prompt: string;
    progress: number;
    status: string;
}

// Fun tips organized by topic keywords
const TIPS_BY_TOPIC: Record<string, string[]> = {
    gradient: [
        "💡 Gradient descent was inspired by how water flows downhill — always seeking the lowest point!",
        "🧠 The learning rate determines how big your steps are. Too big and you might overshoot, too small and you'll take forever!",
        "📉 Local minima are like valleys — gradient descent might get stuck there instead of finding the deepest one.",
        "⚡ Stochastic gradient descent adds randomness to escape local minima and train faster.",
        "🎯 The gradient points in the direction of steepest ascent, so we go the opposite way to minimize!",
    ],
    matrix: [
        "🔢 Matrix multiplication order matters! A×B usually ≠ B×A",
        "💫 The identity matrix is like multiplying by 1 — it leaves everything unchanged.",
        "🎭 Transpose swaps rows and columns, like reflecting over a diagonal mirror.",
        "📊 Eigenvalues reveal how a matrix stretches space in different directions.",
        "🔄 Matrix operations are the backbone of computer graphics, AI, and quantum computing!",
    ],
    algorithm: [
        "⏱️ Big O notation describes how algorithms scale — O(n²) gets slow fast!",
        "🌲 Trees and graphs are everywhere: file systems, social networks, and GPS navigation.",
        "🔍 Binary search is like finding a word in a dictionary — always split in half!",
        "🎲 Randomized algorithms sometimes use luck to solve problems faster.",
        "🏃 Dynamic programming trades memory for speed by remembering previous answers.",
    ],
    binary: [
        "🔍 Binary search eliminates half the possibilities with each comparison!",
        "📚 It only works on sorted data — sorting is the prerequisite.",
        "🎯 With binary search, you can find an item in 1 million elements in just 20 steps!",
        "💻 Computers love binary — everything is 0s and 1s at the lowest level.",
        "🔢 Binary numbers double with each digit: 1, 2, 4, 8, 16...",
    ],
    vector: [
        "➡️ Vectors have both magnitude (length) and direction — that's what makes them special!",
        "➕ Adding vectors is like following directions: go this way, then that way.",
        "📐 The dot product tells you how aligned two vectors are.",
        "✖️ The cross product gives you a vector perpendicular to both inputs!",
        "🎮 Vectors power everything from game physics to machine learning.",
    ],
    neural: [
        "🧠 Neural networks are loosely inspired by how neurons connect in your brain!",
        "🔗 Deep learning just means using many layers — more layers, more abstraction.",
        "⚡ ReLU activation is simple but powerful: if negative, output zero; else, pass through.",
        "📈 Backpropagation is just the chain rule from calculus, applied many times.",
        "🎨 Neural networks can generate art, music, and even write code!",
    ],
    derivative: [
        "📈 The derivative tells you how fast something is changing at any point.",
        "🏔️ Where the derivative is zero, you've found a peak, valley, or plateau!",
        "⚡ The power rule makes derivatives easy: bring down the exponent, subtract one.",
        "🔗 The chain rule handles functions within functions — peel the onion layer by layer.",
        "🚗 Velocity is the derivative of position, acceleration is the derivative of velocity!",
    ],
    physics: [
        "🍎 Newton discovered gravity when an apple fell — or so the legend goes!",
        "⚡ E=mc² means a tiny amount of mass contains enormous energy.",
        "🌊 Light behaves like both a wave and a particle — it depends on how you look!",
        "⏰ Time moves slower near massive objects — GPS satellites must account for this.",
        "🔬 Quantum particles can be in multiple states until you observe them!",
    ],
    default: [
        "✨ Visualizing concepts makes them up to 400% easier to remember!",
        "🎬 Educational videos engage both visual and auditory learning pathways.",
        "🧩 Breaking complex ideas into animations helps build mental models.",
        "🚀 The best explanations use familiar concepts to explain unfamiliar ones.",
        "💡 Understanding beats memorization — you're building intuition right now!",
        "🎯 Active learning through visualization is 6x more effective than passive reading.",
    ],
};

// Get relevant tips based on prompt content
const getTipsForPrompt = (prompt: string): string[] => {
    const lowerPrompt = prompt.toLowerCase();
    const matchedTips: string[] = [];

    // Check each topic keyword
    const topicChecks = [
        { keywords: ['gradient', 'descent', 'learning rate'], topic: 'gradient' },
        { keywords: ['matrix', 'matrices', 'linear algebra'], topic: 'matrix' },
        { keywords: ['algorithm', 'complexity', 'big o'], topic: 'algorithm' },
        { keywords: ['binary', 'search', 'tree'], topic: 'binary' },
        { keywords: ['vector', 'vectors', 'addition'], topic: 'vector' },
        { keywords: ['neural', 'network', 'deep learning', 'ai', 'ml'], topic: 'neural' },
        { keywords: ['derivative', 'calculus', 'differentiation'], topic: 'derivative' },
        { keywords: ['physics', 'force', 'motion', 'energy'], topic: 'physics' },
    ];

    for (const check of topicChecks) {
        if (check.keywords.some(kw => lowerPrompt.includes(kw))) {
            matchedTips.push(...TIPS_BY_TOPIC[check.topic]);
        }
    }

    // If no matches, use default tips
    if (matchedTips.length === 0) {
        return TIPS_BY_TOPIC.default;
    }

    // Shuffle and return
    return matchedTips.sort(() => Math.random() - 0.5);
};

export default function VideoPlayerModal({
    isOpen,
    onClose,
    prompt,
    progress,
    status,
}: VideoPlayerModalProps) {
    const [currentTipIndex, setCurrentTipIndex] = useState(0);
    const [tips, setTips] = useState<string[]>([]);

    // Generate tips based on prompt
    useEffect(() => {
        if (isOpen && prompt) {
            setTips(getTipsForPrompt(prompt));
            setCurrentTipIndex(0);
        }
    }, [isOpen, prompt]);

    // Rotate tips every 5 seconds
    useEffect(() => {
        if (!isOpen || tips.length <= 1) return;

        const interval = setInterval(() => {
            setCurrentTipIndex((prev) => (prev + 1) % tips.length);
        }, 5000);

        return () => clearInterval(interval);
    }, [isOpen, tips.length]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className="relative z-10 w-full max-w-3xl mx-4">
                {/* Video Player Container */}
                <div className="bg-[#0a0a0a] border border-white/[0.1] rounded-2xl overflow-hidden shadow-2xl">
                    {/* Video Frame (16:9 aspect ratio) */}
                    <div className="relative aspect-video bg-gradient-to-br from-[#111] to-[#0a0a0a] flex items-center justify-center">
                        {/* Animated Background Pattern */}
                        <div className="absolute inset-0 opacity-20">
                            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-red-500/20 via-transparent to-transparent animate-pulse" />
                        </div>

                        {/* Buffering Indicator */}
                        <div className="relative flex flex-col items-center gap-6">
                            {/* Circular Progress */}
                            <div className="relative w-28 h-28">
                                {/* Background circle */}
                                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                                    <circle
                                        cx="50"
                                        cy="50"
                                        r="42"
                                        stroke="rgba(255,255,255,0.1)"
                                        strokeWidth="6"
                                        fill="none"
                                    />
                                    {/* Progress circle */}
                                    <circle
                                        cx="50"
                                        cy="50"
                                        r="42"
                                        stroke="url(#progressGradient)"
                                        strokeWidth="6"
                                        fill="none"
                                        strokeLinecap="round"
                                        strokeDasharray={`${2 * Math.PI * 42}`}
                                        strokeDashoffset={`${2 * Math.PI * 42 * (1 - progress / 100)}`}
                                        className="transition-all duration-500"
                                    />
                                    <defs>
                                        <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" stopColor="#F24C4C" />
                                            <stop offset="100%" stopColor="#FF8080" />
                                        </linearGradient>
                                    </defs>
                                </svg>

                                {/* Percentage in center */}
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-3xl font-bold text-white">{progress}%</span>
                                </div>

                                {/* Spinning loader ring */}
                                <div className="absolute inset-0 animate-spin" style={{ animationDuration: '3s' }}>
                                    <svg className="w-full h-full" viewBox="0 0 100 100">
                                        <circle
                                            cx="50"
                                            cy="50"
                                            r="48"
                                            stroke="rgba(242, 76, 76, 0.3)"
                                            strokeWidth="2"
                                            fill="none"
                                            strokeDasharray="30 70"
                                        />
                                    </svg>
                                </div>
                            </div>

                            {/* Status Text */}
                            <div className="text-center">
                                <p className="text-white font-medium text-lg">{status}</p>
                                <p className="text-gray-500 text-sm mt-1">Please wait while we generate your video</p>
                            </div>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="px-6 py-4 border-t border-white/[0.05]">
                        <div className="flex items-center justify-between text-sm mb-2">
                            <span className="text-gray-400">Generation Progress</span>
                            <span className="text-red-400 font-medium">{progress}%</span>
                        </div>
                        <div className="w-full h-2 bg-white/[0.1] rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-red-500 to-pink-400 rounded-full transition-all duration-500"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>

                    {/* Fun Tips Section */}
                    <div className="px-6 py-5 border-t border-white/[0.05] bg-white/[0.02]">
                        <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
                                <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div className="flex-1 min-h-[48px]">
                                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Did you know?</p>
                                <p className="text-gray-300 text-sm leading-relaxed transition-opacity duration-300">
                                    {tips[currentTipIndex] || "✨ Visualizing concepts makes them easier to remember!"}
                                </p>
                            </div>
                        </div>

                        {/* Tip navigation dots */}
                        {tips.length > 1 && (
                            <div className="flex justify-center gap-1.5 mt-4">
                                {tips.slice(0, Math.min(tips.length, 5)).map((_, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setCurrentTipIndex(idx)}
                                        className={`w-1.5 h-1.5 rounded-full transition-all ${idx === currentTipIndex % Math.min(tips.length, 5)
                                            ? 'bg-red-400 w-4'
                                            : 'bg-white/20 hover:bg-white/40'
                                            }`}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Close hint */}
                <p className="text-center text-gray-600 text-xs mt-4">
                    Press <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-gray-400">Esc</kbd> or click outside to minimize
                </p>
            </div>
        </div>
    );
}
