'use client';

import React, { useRef, useEffect, useState } from 'react';
import Link from 'next/link';
import Aurora from '../animations/Aurora';
import BlurText from '../animations/BlurText';

export default function HeroSection() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [isVisible, setIsVisible] = useState(false);
    const [isMuted, setIsMuted] = useState(true);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    setIsVisible(entry.isIntersecting);
                    if (entry.isIntersecting) {
                        videoRef.current?.play();
                    } else {
                        videoRef.current?.pause();
                    }
                });
            },
            { threshold: 0.3 }
        );

        if (containerRef.current) {
            observer.observe(containerRef.current);
        }

        return () => observer.disconnect();
    }, []);

    const toggleMute = () => {
        if (videoRef.current) {
            videoRef.current.muted = !videoRef.current.muted;
            setIsMuted(!isMuted);
        }
    };

    const scrollToHowItWorks = () => {
        const element = document.getElementById('how-it-works');
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-16 overflow-hidden bg-slate-950">
            {/* Aurora Background */}
            <div className="absolute inset-0 opacity-50">
                <Aurora
                    colorStops={['#F24C4C', '#FF5A5A', '#FF8080']}
                    amplitude={1.0}
                    speed={0.5}
                    blend={0.6}
                />
            </div>

            {/* Gradient overlay for depth */}
            <div className="absolute inset-0 bg-gradient-to-b from-slate-950/0 via-slate-950/50 to-slate-950 pointer-events-none" />

            <div className="relative z-10 max-w-5xl mx-auto text-center">
                {/* Hero Content */}
                <div className="mb-12">


                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
                        <BlurText
                            text="Math, explained visually."
                            delay={0.2}
                            duration={1}
                            animateBy="words"
                            direction="bottom"
                        />
                    </h1>
                    <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto mb-10">
                        <BlurText
                            text="Turn questions into beautiful animated explanations."
                            delay={0.6}
                            duration={0.8}
                            animateBy="words"
                        />
                    </p>

                    {/* CTAs */}
                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in" style={{ animationDelay: '1s' }}>
                        <Link
                            href="/app"
                            className="btn-primary"
                        >
                            Generate an Animation
                        </Link>
                        <Link
                            href="/tutor"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full font-medium hover:from-purple-500 hover:to-blue-500 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-purple-500/20"
                        >
                            <span className="text-lg">🎓</span>
                            Try AI Tutor
                        </Link>
                        <button
                            onClick={scrollToHowItWorks}
                            className="btn-secondary"
                        >
                            Watch how it works
                        </button>
                    </div>
                </div>

                {/* Hero Video - Autoplay on scroll with sound toggle */}
                <div
                    ref={containerRef}
                    className="w-full max-w-4xl mx-auto animate-fade-in relative group"
                    style={{ animationDelay: '1.2s' }}
                >
                    <div className="relative rounded-xl overflow-hidden bg-gradient-to-br from-vercel-violet/10 to-vercel-blue/10 border border-white/10 shadow-2xl">
                        <video
                            ref={videoRef}
                            className="w-full h-full object-contain"
                            muted={isMuted}
                            loop
                            playsInline
                            preload="auto"
                        >
                            <source src="/Gradient.mp4" type="video/mp4" />
                        </video>

                        {/* Sound Toggle Button */}
                        <button
                            onClick={toggleMute}
                            className="absolute bottom-4 right-4 p-2 rounded-full bg-black/60 hover:bg-black/80 text-white transition-all opacity-0 group-hover:opacity-100 backdrop-blur-sm border border-white/10"
                            aria-label={isMuted ? 'Unmute' : 'Mute'}
                        >
                            {isMuted ? (
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                </svg>
                            )}
                        </button>
                    </div>
                    <p className="text-gray-500 text-sm mt-4">
                        Generated with Nimator: Gradient Descent Visualization
                    </p>
                </div>
            </div>

            {/* Scroll Indicator */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce z-10">
                <svg
                    className="w-6 h-6 text-gray-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                </svg>
            </div>
        </section>
    );
}
