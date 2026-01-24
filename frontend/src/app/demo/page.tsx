'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function DemoPage() {
    const [isPlaying, setIsPlaying] = useState(false);

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
            {/* Header */}
            <div className="sticky top-0 z-10 bg-black/50 backdrop-blur-xl border-b border-white/10">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                                <span className="text-2xl">🎓</span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                                    Visual Explainer Generator
                                </h1>
                                <p className="text-sm text-gray-400">AI-Powered Educational Animations</p>
                            </div>
                        </Link>
                    </div>
                    <div className="flex items-center gap-3">
                        <Link
                            href="/tutor"
                            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-lg text-sm font-medium transition-all"
                        >
                            <span>🎓</span>
                            Try AI Tutor
                        </Link>
                        <Link
                            href="/app"
                            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-all"
                        >
                            <span>🎬</span>
                            Generate Video
                        </Link>
                        <span className="px-3 py-1.5 bg-green-500/20 border border-green-500/30 rounded-full text-green-400 text-sm font-medium">
                            ● Live Demo
                        </span>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Chat Panel */}
                    <div className="lg:col-span-1">
                        <div className="bg-gray-800/50 backdrop-blur rounded-2xl border border-white/10 overflow-hidden h-[650px] flex flex-col">
                            {/* Chat Header */}
                            <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
                                <h2 className="font-bold text-lg flex items-center gap-2">
                                    💬 Conversation
                                </h2>
                            </div>

                            {/* Messages */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                                {/* Welcome Message */}
                                <div className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center flex-shrink-0">
                                        🤖
                                    </div>
                                    <div className="bg-gray-700/50 rounded-2xl rounded-tl-none px-4 py-3 max-w-[90%]">
                                        <p className="text-sm text-gray-300">
                                            Hello! I am your AI tutor. Ask me anything about <strong className="text-blue-400">mathematics</strong>, <strong className="text-purple-400">physics</strong>, or <strong className="text-green-400">machine learning</strong>!
                                        </p>
                                    </div>
                                </div>

                                {/* User Message */}
                                <div className="flex gap-3 justify-end">
                                    <div className="bg-blue-600 rounded-2xl rounded-tr-none px-4 py-3 max-w-[90%]">
                                        <p className="text-sm">Explain gradient descent visually</p>
                                    </div>
                                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                                        👤
                                    </div>
                                </div>

                                {/* AI Response */}
                                <div className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center flex-shrink-0">
                                        🤖
                                    </div>
                                    <div className="bg-gray-700/50 rounded-2xl rounded-tl-none px-4 py-3 max-w-[90%]">
                                        <p className="text-sm text-gray-300 mb-2">
                                            <strong className="text-white">Gradient Descent</strong> is an optimization algorithm that finds the minimum of a function.
                                        </p>
                                        <p className="text-sm text-gray-300 mb-2">
                                            Think of it like a <span className="text-yellow-400">ball rolling down a hill</span> - it always moves toward the lowest point!
                                        </p>
                                        <p className="text-sm text-gray-400 italic">
                                            🎬 Generating visual explanation...
                                        </p>
                                    </div>
                                </div>

                                {/* Video Ready Indicator */}
                                <div className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0 animate-pulse">
                                        ✓
                                    </div>
                                    <div className="bg-green-500/20 border border-green-500/30 rounded-2xl rounded-tl-none px-4 py-3 max-w-[90%]">
                                        <p className="text-sm text-green-400">
                                            Video ready! Watch the animation →
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Input Area - Demo Mode */}
                            <div className="border-t border-white/10 p-4 bg-gray-900/50">
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        placeholder="Demo mode - try the live version!"
                                        disabled
                                        className="flex-1 px-4 py-3 bg-gray-700/50 text-gray-500 rounded-xl border border-white/10 text-sm cursor-not-allowed"
                                    />
                                    <button disabled className="px-4 py-3 bg-gray-600 text-gray-400 rounded-xl font-semibold cursor-not-allowed">
                                        Send
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Content Panel */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Explanation Panel */}
                        <div className="bg-gray-800/50 backdrop-blur rounded-2xl border border-white/10 p-6">
                            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                📖 <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Explanation</span>
                            </h2>
                            
                            <div className="space-y-4 text-gray-300">
                                <h3 className="text-lg font-semibold text-white">What is Gradient Descent?</h3>
                                <p>
                                    <strong className="text-blue-400">Gradient Descent</strong> is an optimization algorithm used to minimize a function by iteratively moving in the direction of steepest descent.
                                </p>
                                
                                <h4 className="font-semibold text-white mt-4">Key Concepts:</h4>
                                <ul className="list-disc list-inside space-y-2 text-sm">
                                    <li><strong className="text-yellow-400">The Landscape:</strong> Imagine a mountain representing the loss function</li>
                                    <li><strong className="text-green-400">The Goal:</strong> Find the valley (minimum) where error is smallest</li>
                                    <li><strong className="text-purple-400">The Gradient:</strong> The slope tells us which way is down</li>
                                    <li><strong className="text-pink-400">Learning Rate:</strong> Controls how big each step is</li>
                                </ul>

                                <div className="bg-gray-900/50 rounded-xl p-4 mt-4 border border-white/5">
                                    <p className="text-sm font-mono text-green-400">
                                        New Weight = Old Weight - Learning Rate × Gradient
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Video Panel */}
                        <div className="bg-gray-800/50 backdrop-blur rounded-2xl border border-white/10 overflow-hidden">
                            <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
                                <h2 className="font-bold text-lg flex items-center gap-2">
                                    🎬 Gradient Descent Visualization
                                </h2>
                            </div>
                            <div className="aspect-video bg-gradient-to-br from-gray-900 via-purple-900/50 to-gray-900 relative">
                                {!isPlaying ? (
                                    <div
                                        className="absolute inset-0 flex flex-col items-center justify-center cursor-pointer group"
                                        onClick={() => setIsPlaying(true)}
                                    >
                                        <div className="w-24 h-24 rounded-full bg-white/10 backdrop-blur flex items-center justify-center group-hover:bg-white/20 transition-all group-hover:scale-110">
                                            <div className="w-0 h-0 border-t-[20px] border-t-transparent border-l-[35px] border-l-white border-b-[20px] border-b-transparent ml-2" />
                                        </div>
                                        <p className="text-white font-semibold mt-4">Click to Play Animation</p>
                                        <p className="text-gray-400 text-sm mt-1">Generated by Manim + AI</p>
                                    </div>
                                ) : (
                                    <div className="absolute inset-0 p-8">
                                        {/* Animated Gradient Descent SVG */}
                                        <svg viewBox="0 0 400 250" className="w-full h-full">
                                            <defs>
                                                <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                                    <stop offset="0%" stopColor="#ef4444" stopOpacity="0.3" />
                                                    <stop offset="50%" stopColor="#eab308" stopOpacity="0.2" />
                                                    <stop offset="100%" stopColor="#22c55e" stopOpacity="0.3" />
                                                </linearGradient>
                                                <filter id="glow">
                                                    <feGaussianBlur stdDeviation="4" result="blur" />
                                                    <feMerge>
                                                        <feMergeNode in="blur" />
                                                        <feMergeNode in="SourceGraphic" />
                                                    </feMerge>
                                                </filter>
                                            </defs>

                                            {/* Background gradient surface */}
                                            <rect width="400" height="250" fill="url(#bgGrad)" rx="8" />

                                            {/* Contour lines */}
                                            {[40, 60, 80, 100].map((r, i) => (
                                                <ellipse
                                                    key={i}
                                                    cx="300"
                                                    cy="180"
                                                    rx={r}
                                                    ry={r * 0.5}
                                                    fill="none"
                                                    stroke="white"
                                                    strokeWidth="1"
                                                    opacity={0.15 - i * 0.03}
                                                />
                                            ))}

                                            {/* Descent path */}
                                            <path
                                                d="M 80 50 Q 120 80 160 100 T 220 140 T 280 170 T 300 180"
                                                fill="none"
                                                stroke="white"
                                                strokeWidth="2"
                                                strokeDasharray="300"
                                                strokeDashoffset="300"
                                                opacity="0.6"
                                            >
                                                <animate
                                                    attributeName="stroke-dashoffset"
                                                    from="300"
                                                    to="0"
                                                    dur="3s"
                                                    fill="freeze"
                                                    repeatCount="indefinite"
                                                />
                                            </path>

                                            {/* Animated ball */}
                                            <circle cx="80" cy="50" r="12" fill="white" filter="url(#glow)">
                                                <animate
                                                    attributeName="cx"
                                                    values="80;160;220;280;300"
                                                    dur="3s"
                                                    repeatCount="indefinite"
                                                />
                                                <animate
                                                    attributeName="cy"
                                                    values="50;100;140;170;180"
                                                    dur="3s"
                                                    repeatCount="indefinite"
                                                />
                                                <animate
                                                    attributeName="r"
                                                    values="12;10;9;8;7"
                                                    dur="3s"
                                                    repeatCount="indefinite"
                                                />
                                            </circle>

                                            {/* Minimum point */}
                                            <circle cx="300" cy="180" r="8" fill="#22c55e" filter="url(#glow)" />
                                            <text x="300" y="210" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
                                                Global Minimum
                                            </text>

                                            {/* Start label */}
                                            <text x="80" y="35" textAnchor="middle" fill="white" fontSize="10" opacity="0.8">
                                                Start
                                            </text>

                                            {/* Title */}
                                            <text x="200" y="25" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">
                                                Gradient Descent in Action
                                            </text>
                                        </svg>

                                        <button
                                            onClick={() => setIsPlaying(false)}
                                            className="absolute top-4 right-4 px-4 py-2 bg-red-500/80 hover:bg-red-500 rounded-lg text-sm font-medium transition-colors"
                                        >
                                            ⏹ Stop
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Video Stats */}
                            <div className="bg-gray-900/50 px-6 py-4 grid grid-cols-4 gap-4 text-center text-sm border-t border-white/5">
                                <div>
                                    <p className="text-gray-500">Duration</p>
                                    <p className="font-semibold">2:30</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">FPS</p>
                                    <p className="font-semibold">60</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Quality</p>
                                    <p className="font-semibold">1080p</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Engine</p>
                                    <p className="font-semibold">Manim</p>
                                </div>
                            </div>
                        </div>

                        {/* Tech Stack Cards */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl p-5 border border-blue-500/20">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-2xl">🧠</span>
                                    <h3 className="font-bold text-blue-400">DeepSeek V3.2</h3>
                                </div>
                                <p className="text-sm text-gray-400">Generates clear explanations with visual-first pedagogy</p>
                            </div>
                            <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-5 border border-purple-500/20">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-2xl">🎨</span>
                                    <h3 className="font-bold text-purple-400">Qwen Coder 32B</h3>
                                </div>
                                <p className="text-sm text-gray-400">Creates Manim animation code synced with explanations</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-12 bg-black/50 border-t border-white/10 py-8">
                <div className="max-w-7xl mx-auto px-6 text-center">
                    <p className="text-lg font-semibold mb-2">Visual Explainer Generator</p>
                    <p className="text-gray-400 text-sm mb-6">
                        Multi-Agent Architecture: DeepSeek (Reasoning) → Qwen (Code) → Manim (Render) → Deepgram (Voice)
                    </p>
                    <div className="flex justify-center gap-6">
                        <Link
                            href="/tutor"
                            className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors"
                        >
                            <span>🎓</span>
                            AI Tutor
                        </Link>
                        <Link
                            href="/app"
                            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
                        >
                            <span>🎬</span>
                            Video Generator
                        </Link>
                        <Link
                            href="/"
                            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                        >
                            <span>🏠</span>
                            Home
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
