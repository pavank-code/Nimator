'use client';

import React, { useEffect, useRef } from 'react';

const TESTIMONIALS = [
    {
        quote: "Finally, a tool that lets me focus on explaining concepts instead of wrestling with animation software.",
        author: "Math Educator",
        role: "High School Teacher",
    },
    {
        quote: "I used to spend hours making animations for my YouTube videos. Now it takes minutes.",
        author: "Content Creator",
        role: "Educational YouTuber",
    },
    {
        quote: "The quality of the animations rivals professional studios. This changes everything for online education.",
        author: "EdTech Founder",
        role: "Startup CEO",
    },
];

export default function Testimonials() {
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
            className="section-spacing bg-slate-900"
        >
            <div className="max-w-6xl mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <p className="reveal text-purple-400 text-sm font-medium tracking-widest uppercase mb-4">
                        What people are saying
                    </p>
                    <h2 className="reveal reveal-delay-1 text-3xl md:text-4xl font-semibold text-white">
                        Trusted by educators worldwide
                    </h2>
                </div>

                {/* Testimonials Grid */}
                <div className="grid md:grid-cols-3 gap-8">
                    {TESTIMONIALS.map((testimonial, index) => (
                        <div
                            key={index}
                            className={`reveal reveal-delay-${index + 2} p-8 rounded-2xl bg-slate-800/50 border border-white/5`}
                        >
                            {/* Quote */}
                            <div className="mb-6">
                                <svg className="w-8 h-8 text-purple-400/50 mb-4" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                                </svg>
                                <p className="text-gray-300 leading-relaxed">
                                    &quot;{testimonial.quote}&quot;
                                </p>
                            </div>

                            {/* Author */}
                            <div className="border-t border-white/10 pt-6">
                                <p className="text-white font-medium">{testimonial.author}</p>
                                <p className="text-gray-500 text-sm">{testimonial.role}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
