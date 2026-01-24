'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const STEPS = [
    {
        title: 'Interprets mathematical structure',
        description: 'The system parses your natural language input and identifies the underlying mathematical concepts, relationships, and operations.',
    },
    {
        title: 'Builds a visual reasoning graph',
        description: 'Mathematical elements are mapped to visual primitives—shapes, transformations, and relationships that can be animated.',
    },
    {
        title: 'Translates ideas into motion primitives',
        description: 'Each concept is converted into animation instructions: what appears, how it moves, when it transforms.',
    },
    {
        title: 'Renders scenes programmatically',
        description: 'Using Manim under the hood, scenes are rendered with mathematical precision and visual clarity.',
    },
];

export default function BehindTheScenes() {
    const sectionRef = useRef<HTMLElement>(null);
    const [openIndex, setOpenIndex] = useState<number | null>(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setIsVisible(true);
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
            <div className="max-w-3xl mx-auto px-6">
                {/* Section Header */}
                <motion.div
                    className="text-center mb-12"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isVisible ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6 }}
                >
                    <p className="text-purple-400 text-sm font-medium tracking-widest uppercase mb-4">
                        For the curious
                    </p>
                    <h2 className="text-3xl md:text-4xl font-semibold text-white">
                        How the system thinks
                    </h2>
                </motion.div>

                {/* Accordion */}
                <motion.div
                    className="space-y-3"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isVisible ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6, delay: 0.2 }}
                >
                    {STEPS.map((step, index) => (
                        <div
                            key={index}
                            className="border border-gray-800 rounded-xl overflow-hidden bg-slate-900/50"
                        >
                            <button
                                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                                className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-slate-800/50 transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <span className="text-purple-400 font-mono text-sm">
                                        {String(index + 1).padStart(2, '0')}
                                    </span>
                                    <span className="text-white font-medium">
                                        {step.title}
                                    </span>
                                </div>
                                <motion.div
                                    animate={{ rotate: openIndex === index ? 180 : 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="text-gray-400"
                                >
                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </motion.div>
                            </button>

                            <AnimatePresence>
                                {openIndex === index && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        transition={{ duration: 0.3 }}
                                        className="overflow-hidden"
                                    >
                                        <p className="px-6 pb-5 pl-16 text-gray-400 leading-relaxed">
                                            {step.description}
                                        </p>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </motion.div>

                {/* Key Line */}
                <motion.p
                    className="text-center text-gray-500 mt-10 text-sm"
                    initial={{ opacity: 0 }}
                    animate={isVisible ? { opacity: 1 } : {}}
                    transition={{ duration: 0.6, delay: 0.4 }}
                >
                    No timelines. No keyframes. No manual tweaking.
                </motion.p>
            </div>
        </section>
    );
}
