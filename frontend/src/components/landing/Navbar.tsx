'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Dock from '../animations/Dock';

export default function Navbar() {
    const [scrolled, setScrolled] = useState(false);
    const [showDock, setShowDock] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 10);
            // Show dock after scrolling past hero
            setShowDock(window.scrollY > window.innerHeight * 0.5);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const dockItems = [
        {
            label: 'Home',
            href: '/',
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
            ),
        },
        {
            label: 'AI Tutor',
            href: '/tutor',
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
            ),
        },
        {
            label: 'How it Works',
            href: '#how-it-works',
            onClick: () => scrollToSection('how-it-works'),
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            ),
        },
        {
            label: 'Examples',
            href: '#examples',
            onClick: () => scrollToSection('examples'),
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            ),
        },
        {
            label: 'Try Free',
            href: '/app',
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            ),
        },
    ];

    return (
        <>
            {/* Standard Navbar */}
            <nav
                className={`fixed top-0 left-0 right-0 z-50 h-16 transition-all duration-300 ${scrolled
                    ? 'bg-slate-950/90 backdrop-blur-xl border-b border-white/5'
                    : 'bg-transparent'
                    } ${showDock ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}
            >
                <div className="max-w-6xl mx-auto px-6 h-full flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <img
                            src="/logo_128.png"
                            alt="Nimator"
                            className="h-8 w-8"
                        />
                        <span className="text-white font-semibold text-lg tracking-tight">Nimator</span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center gap-8">
                        <Link
                            href="/tutor"
                            className="text-sm text-gray-400 hover:text-white transition-colors duration-200 flex items-center gap-1"
                        >
                            <span className="text-lg">🎓</span>
                            AI Tutor
                        </Link>
                        <button
                            onClick={() => scrollToSection('how-it-works')}
                            className="text-sm text-gray-400 hover:text-white transition-colors duration-200"
                        >
                            How it Works
                        </button>
                        <button
                            onClick={() => scrollToSection('examples')}
                            className="text-sm text-gray-400 hover:text-white transition-colors duration-200"
                        >
                            Examples
                        </button>
                        <button
                            onClick={() => scrollToSection('philosophy')}
                            className="text-sm text-gray-400 hover:text-white transition-colors duration-200"
                        >
                            About
                        </button>
                    </div>

                    {/* CTA Button */}
                    <Link
                        href="/app"
                        className="px-5 py-2 text-sm font-medium text-white border border-white/20 rounded-full hover:bg-white hover:text-slate-900 transition-all"
                    >
                        Try Free
                    </Link>
                </div>
            </nav>

            {/* Floating Dock (appears after scrolling) */}
            {showDock && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
                    <Dock items={dockItems} magnification={1.3} baseSize={52} />
                </div>
            )}
        </>
    );
}
