'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import ElectricBorder from '../animations/ElectricBorder';
import Dither from '../animations/Dither';
import Spotlight from '../animations/Spotlight';

export default function ProductShowcase() {
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
            id="examples"
            className="relative section-spacing-lg bg-black overflow-hidden"
        >
            {/* Dither Background with Vercel Colors */}
            <div className="absolute inset-0 opacity-20">
                <Dither
                    density={1.2}
                    speed={0.2}
                    colors={['#0070F3', '#7928CA', '#50E3C2']}
                />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-24">
                    <h2 className="reveal text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                        See what's possible
                    </h2>
                </div>

                {/* Intro paragraph */}
                <div className="reveal reveal-delay-1 text-center mb-32">
                    <p className="text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed font-light">
                        Every concept has a shape.
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500 font-medium">We help you discover it.</span>
                    </p>
                </div>

                {/* Example Categories with Electric Border */}
                <div className="reveal reveal-delay-2 grid md:grid-cols-3 gap-8">
                    {[
                        { title: 'Linear Algebra', description: 'Vectors, matrices, transformations', coming: true },
                        { title: 'Calculus', description: 'Derivatives, integrals, limits', coming: true },
                        { title: 'Optimization', description: 'Gradient descent, convergence', available: true },
                    ].map((item, index) => (
                        <ElectricBorder
                            key={item.title}
                            borderRadius={12}
                            borderWidth={1}
                            gradientColors={
                                item.available
                                    ? ['#0070F3', '#7928CA', '#50E3C2', '#0070F3']
                                    : ['#333333', '#111111', '#333333', '#333333']
                            }
                            animationSpeed={item.available ? 3 : 10}
                        >
                            <div className="group p-8 rounded-xl bg-black border border-white/10 h-full hover:border-white/20 transition-all">
                                <h3 className="text-xl font-bold text-white mb-3">
                                    {item.title}
                                </h3>
                                <p className="text-gray-400 text-base mb-6 leading-relaxed">
                                    {item.description}
                                </p>
                                {item.available ? (
                                    <Link
                                        href="/app"
                                        className="inline-flex items-center gap-2 text-white text-sm font-medium hover:text-vercel-cyan transition-colors"
                                    >
                                        Try now
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                        </svg>
                                    </Link>
                                ) : (
                                    <span className="text-xs font-mono px-2 py-1 rounded border border-gray-800 text-gray-500 uppercase tracking-widest">
                                        Coming soon
                                    </span>
                                )}
                            </div>
                        </ElectricBorder>
                    ))}
                </div>
            </div>
        </section>
    );
}
