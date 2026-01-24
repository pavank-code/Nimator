'use client';

import React from 'react';
import Link from 'next/link';
import ChromaGrid from '../animations/ChromaGrid';
import BlurText from '../animations/BlurText';
import BorderBeam from '../animations/BorderBeam';

export default function FinalCTA() {
    return (
        <section className="relative section-spacing-lg overflow-hidden bg-slate-950">
            {/* ChromaGrid Background */}
            <div className="absolute inset-0">
                <ChromaGrid
                    cellSize={80}
                    gap={6}
                    colors={['#F24C4C', '#FF5A5A', '#FF8080', '#D93030', '#FFA0A0']}
                    speed={1.2}
                />
            </div>

            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-slate-950" />

            {/* Content */}
            <div className="relative z-10 max-w-2xl mx-auto px-6 text-center">
                <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                    <BlurText
                        text="Start visualizing math today"
                        delay={0}
                        duration={0.8}
                        animateBy="words"
                    />
                </h2>
                <p className="text-xl md:text-2xl text-gray-400 mb-10 font-light">
                    See your first animation in under a minute.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                    <div className="relative inline-block group">
                        <Link
                            href="/app"
                            className="relative z-10 inline-flex items-center gap-2 px-10 py-4 bg-white text-slate-900 rounded-full font-medium text-lg hover:bg-gray-100 transition-all hover:scale-105 active:scale-95"
                        >
                            Generate Video
                            <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </svg>
                        </Link>
                        <BorderBeam
                            duration={8}
                            size={150}
                            colorFrom="#FF5A5A"
                            colorTo="#F24C4C"
                            className="rounded-full pointer-events-none"
                            borderWidth={3}
                        />
                    </div>
                    <Link
                        href="/tutor"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full font-medium text-lg hover:from-purple-500 hover:to-blue-500 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-purple-500/30"
                    >
                        <span className="text-xl">🎓</span>
                        AI Tutor
                        <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                    </Link>
                </div>
            </div>
        </section>
    );
}
