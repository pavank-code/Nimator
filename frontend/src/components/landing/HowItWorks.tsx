'use client';

import React, { useEffect, useRef } from 'react';
import ColourBends from '../animations/ColourBends';
import Spotlight from '../animations/Spotlight';

const STEPS = [
    {
        number: '01',
        title: 'Ask a question',
        description: 'Type a math concept in plain language.',
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        ),
    },
    {
        number: '02',
        title: 'The system understands',
        description: 'Mathematical structure is analyzed and mapped visually.',
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
        ),
    },
    {
        number: '03',
        title: 'Animation is generated',
        description: 'Scenes render programmatically with clarity and motion.',
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
            </svg>
        ),
    },
    {
        number: '04',
        title: 'Export & share',
        description: 'High-quality video, ready to teach.',
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
        ),
    },
];

export default function HowItWorks() {
    const sectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.querySelectorAll('.reveal').forEach((el, index) => {
                            setTimeout(() => {
                                el.classList.add('visible');
                            }, index * 100);
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
            id="how-it-works"
            className="relative section-spacing-lg overflow-hidden bg-slate-950"
        >
            {/* Colour Bends Background */}
            <div className="absolute inset-0">
                <ColourBends
                    colors={['#F24C4C', '#FF5A5A', '#FF8080', '#FFA0A0']}
                    speed={0.6}
                    opacity={0.15}
                />
            </div>

            <div className="relative z-10 max-w-6xl mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <h2 className="reveal text-3xl md:text-4xl font-semibold text-white mb-4">
                        How it works
                    </h2>
                    <p className="reveal reveal-delay-1 text-xl text-gray-400 max-w-xl mx-auto">
                        From question to animation in seconds
                    </p>
                </div>

                {/* Steps Grid */}
                <div className="grid md:grid-cols-4 gap-6">
                    {STEPS.map((step, index) => (
                        <div
                            key={step.number}
                            className={`reveal reveal-delay-${index + 1}`}
                        >
                            <Spotlight className="h-full p-6 bg-zinc-900/50">
                                {/* Step Number */}
                                <span className="text-white/40 text-sm font-mono mb-4 block">
                                    {step.number}
                                </span>

                                {/* Icon */}
                                <div className="text-white mb-4">
                                    {step.icon}
                                </div>

                                {/* Content */}
                                <h3 className="text-lg font-bold text-white mb-2">
                                    {step.title}
                                </h3>
                                <p className="text-gray-400 text-sm leading-relaxed font-light">
                                    {step.description}
                                </p>
                            </Spotlight>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
