'use client';

import React, { useEffect, useRef } from 'react';
import Spotlight from '../animations/Spotlight';

const TRADITIONAL = [
    'Steep learning curve',
    'Manual scene design',
    'Time-consuming workflows',
    'Code-heavy approach',
    'Technical barrier to entry',
];

const NIMATOR = [
    'Natural language input',
    'Automatic scene planning',
    'Idea-first animations',
    'No coding required',
    'Instant results',
];

export default function WhatMakesDifferent() {
    const sectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.querySelectorAll('.reveal').forEach((el, index) => {
                            setTimeout(() => {
                                el.classList.add('visible');
                            }, index * 80);
                        });
                    }
                });
            },
            { threshold: 0.1 }
        );

        if (sectionRef.current) {
            observer.observe(sectionRef.current);
        }

        return () => observer.disconnect();
    }, []);

    return (
        <section
            ref={sectionRef}
            className="section-spacing-lg bg-black"
        >
            <div className="max-w-6xl mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-20">
                    <p className="reveal text-nimator-red text-sm font-semibold tracking-widest uppercase mb-4">
                        The New Standard
                    </p>
                    <h2 className="reveal reveal-delay-1 text-3xl md:text-5xl font-bold text-white tracking-tight">
                        Why creators switch
                    </h2>
                </div>

                {/* Comparison Grid */}
                <div className="grid md:grid-cols-2 gap-8 md:gap-12">
                    {/* Traditional Tools */}
                    <div className="reveal reveal-delay-2 h-full">
                        <Spotlight className="h-full p-10 bg-zinc-900/30 border-white/5" fill="rgba(255, 0, 0, 0.05)">
                            <h3 className="text-xl font-medium text-gray-400 mb-8 flex items-center gap-3">
                                <span className="p-2 rounded-lg bg-red-500/10 text-red-400">
                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </span>
                                Traditional Tools
                            </h3>
                            <ul className="space-y-6">
                                {TRADITIONAL.map((item, index) => (
                                    <li key={index} className="flex items-start gap-4 text-gray-500">
                                        <div className="mt-1 w-1.5 h-1.5 rounded-full bg-red-500/20 shrink-0" />
                                        <span className="text-lg font-light">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </Spotlight>
                    </div>

                    {/* Nimator */}
                    <div className="reveal reveal-delay-3 h-full">
                        <Spotlight className="h-full p-10 bg-zinc-900/80 border-nimator-red/20" fill="rgba(242, 76, 76, 0.15)">
                            <h3 className="text-xl font-medium text-white mb-8 flex items-center gap-3">
                                <span className="p-2 rounded-lg bg-nimator-red/10 text-nimator-red">
                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </span>
                                Nimator
                            </h3>
                            <ul className="space-y-6">
                                {NIMATOR.map((item, index) => (
                                    <li key={index} className="flex items-start gap-4 text-gray-300">
                                        <div className="mt-1 w-1.5 h-1.5 rounded-full bg-nimator-red shrink-0 shadow-[0_0_10px_rgba(242,76,76,0.5)]" />
                                        <span className="text-lg font-medium">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </Spotlight>
                    </div>
                </div>

                {/* Key Line */}
                <div className="reveal mt-24 text-center">
                    <p className="text-2xl md:text-4xl font-light text-gray-400 leading-relaxed max-w-4xl mx-auto">
                        Stop fighting with keyframes.
                        <br />
                        <span className="text-white font-medium">Start explaining with code.</span>
                    </p>
                </div>
            </div>
        </section>
    );
}
