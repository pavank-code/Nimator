'use client';

import React, { useEffect, useRef } from 'react';
import BlurText from '../animations/BlurText';

export default function WhyThisExists() {
    const sectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.querySelectorAll('.reveal').forEach((el, index) => {
                            setTimeout(() => {
                                el.classList.add('visible');
                            }, index * 150);
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
            className="section-spacing-lg bg-slate-950"
        >
            <div className="max-w-2xl mx-auto px-6 text-center">
                <p className="reveal text-purple-400 text-sm font-medium tracking-widest uppercase mb-8">
                    Why we built this
                </p>

                <div className="reveal reveal-delay-1 space-y-8">
                    <p className="text-2xl md:text-3xl font-light text-white leading-relaxed">
                        Math is not hard because it is abstract.
                    </p>
                    <p className="text-2xl md:text-3xl font-semibold text-white leading-relaxed">
                        It is hard because it is{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                            invisible
                        </span>.
                    </p>
                </div>

                <div className="reveal reveal-delay-2 mt-16 space-y-4">
                    <p className="text-lg text-gray-400 leading-relaxed">
                        We believe understanding begins when ideas can be seen.
                    </p>
                    <p className="text-lg text-gray-300 leading-relaxed">
                        Nimator exists to turn mental models into motion—
                        <span className="text-white font-medium">instantly</span>.
                    </p>
                </div>
            </div>
        </section>
    );
}
