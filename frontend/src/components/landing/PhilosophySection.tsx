'use client';

import React, { useEffect, useRef } from 'react';
import FluidGlass from '../animations/FluidGlass';
import BlurText from '../animations/BlurText';
import GradientText from '../animations/GradientText';

export default function PhilosophySection() {
    const sectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.querySelectorAll('.reveal').forEach((el) => {
                            el.classList.add('visible');
                        });
                    }
                });
            },
            { threshold: 0.2 }
        );

        if (sectionRef.current) {
            observer.observe(sectionRef.current);
        }

        return () => observer.disconnect();
    }, []);

    return (
        <section
            ref={sectionRef}
            id="philosophy"
            className="section-spacing-lg bg-black"
        >
            <div className="max-w-6xl mx-auto px-6">
                <div className="grid md:grid-cols-2 gap-24 items-center">
                    {/* Text Content */}
                    <div>
                        <h2 className="text-3xl md:text-5xl font-bold text-white mb-8 tracking-tight">
                            <BlurText
                                text="Designed for"
                                delay={0}
                                duration={0.8}
                                animateBy="words"
                            />
                            {' '}
                            <GradientText
                                text="focus"
                                colors={['#0070F3', '#7928CA', '#50E3C2', '#0070F3']}
                                animationSpeed={3}
                            />
                        </h2>
                        <div className="reveal reveal-delay-1 space-y-6">
                            <p className="text-xl text-gray-400 leading-relaxed font-light">
                                Our platform removes friction between curiosity and understanding.
                            </p>
                            <p className="text-xl text-gray-400 leading-relaxed font-light">
                                <span className="text-white font-medium">No timelines. No keyframes. No complexity.</span>
                            </p>
                            <p className="text-xl text-white font-medium leading-relaxed">
                                Just ideas—made visible.
                            </p>
                        </div>
                    </div>

                    {/* Visual Element with Fluid Glass */}
                    <div className="reveal reveal-delay-2">
                        <FluidGlass
                            className="rounded-3xl p-12 bg-white/5 border border-white/10"
                            intensity={0.4}
                            blur={20}
                            tint="rgba(0, 112, 243, 0.05)"
                        >
                            <div className="relative">
                                {/* Abstract line animation representation */}
                                <svg
                                    viewBox="0 0 400 300"
                                    className="w-full h-auto drop-shadow-2xl"
                                    fill="none"
                                >
                                    {/* Animated curves representing math concepts */}
                                    <path
                                        d="M 50 150 Q 100 50 200 150 Q 300 250 350 150"
                                        stroke="url(#gradient1)"
                                        strokeWidth="4"
                                        strokeLinecap="round"
                                        className="opacity-90"
                                        style={{
                                            strokeDasharray: 600,
                                            strokeDashoffset: 0,
                                            animation: 'draw 3s ease-in-out infinite alternate'
                                        }}
                                    />
                                    <path
                                        d="M 50 200 Q 150 100 250 200 Q 350 300 400 200"
                                        stroke="url(#gradient2)"
                                        strokeWidth="3"
                                        strokeLinecap="round"
                                        className="opacity-70"
                                        style={{
                                            strokeDasharray: 500,
                                            strokeDashoffset: 0,
                                            animation: 'draw 4s ease-in-out 0.5s infinite alternate'
                                        }}
                                    />
                                    {/* Gradients */}
                                    <defs>
                                        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" stopColor="#0070F3" />
                                            <stop offset="100%" stopColor="#7928CA" />
                                        </linearGradient>
                                        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" stopColor="#7928CA" />
                                            <stop offset="100%" stopColor="#50E3C2" />
                                        </linearGradient>
                                    </defs>
                                    {/* Dots */}
                                    <circle cx="200" cy="150" r="8" fill="#8b5cf6" className="opacity-90" />
                                    <circle cx="100" cy="100" r="4" fill="#ec4899" className="opacity-70" />
                                    <circle cx="300" cy="200" r="6" fill="#ffffff" className="opacity-50" />
                                </svg>

                                <style jsx>{`
                  @keyframes draw {
                    0% {
                      stroke-dashoffset: 600;
                    }
                    100% {
                      stroke-dashoffset: 0;
                    }
                  }
                `}</style>
                            </div>
                        </FluidGlass>
                    </div>
                </div>
            </div>
        </section>
    );
}
