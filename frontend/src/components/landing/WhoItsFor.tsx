'use client';

import React, { useEffect, useRef } from 'react';
import Spotlight from '../animations/Spotlight';
import TiltedCard from '../animations/TiltedCard';

const PERSONAS = [
    {
        title: 'Students',
        description: 'Learn visually. Understand faster.',
    },
    {
        title: 'Educators',
        description: 'Create explanations in minutes, not days.',
    },
    {
        title: 'Content Creators',
        description: 'Produce math videos without animation skills.',
    },
    {
        title: 'Developers & EdTech',
        description: 'Embed dynamic math visuals into products.',
    },
];

export default function WhoItsFor() {
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
            className="section-spacing bg-black"
        >
            <div className="max-w-6xl mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <h2 className="reveal text-3xl md:text-5xl font-bold text-white mb-4">
                        Built for people who explain ideas
                    </h2>
                </div>

                {/* Personas Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                    {PERSONAS.map((persona, index) => (
                        <div
                            key={persona.title}
                            className={`reveal reveal-delay-${index + 1}`}
                        >
                            <TiltedCard rotateAmplitude={8} scaleOnHover={1.05} className="h-full">
                                <Spotlight className="h-full p-8 bg-zinc-900/50 border-white/5 flex flex-col items-center text-center group cursor-default">
                                    <div className="mb-4 p-3 rounded-full bg-white/5 group-hover:bg-nimator-red/10 group-hover:text-nimator-red transition-colors text-white">
                                        {/* Icon based on index */}
                                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            {index === 0 && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />}
                                            {index === 1 && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />}
                                            {index === 2 && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />}
                                            {index === 3 && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />}
                                        </svg>
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-3 tracking-tight">
                                        {persona.title}
                                    </h3>
                                    <p className="text-gray-400 text-sm leading-relaxed font-light">
                                        {persona.description}
                                    </p>
                                </Spotlight>
                            </TiltedCard>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
