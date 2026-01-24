'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChromaGrid from '../animations/ChromaGrid';

const FAQS = [
    {
        question: 'How does Nimator generate animations?',
        answer: 'Nimator uses AI to understand your mathematical concept, then programmatically generates animations using Manim (the same library used by 3Blue1Brown). The entire process is automated—no coding or animation skills required.',
    },
    {
        question: 'What topics can I visualize?',
        answer: 'Currently, Nimator works best with mathematical and scientific concepts: algebra, calculus, linear algebra, probability, algorithms, and physics. We\'re continuously expanding our capabilities.',
    },
    {
        question: 'Is Nimator free to use?',
        answer: 'Yes! Nimator is completely free to use with no credit card required. We believe everyone should have access to high-quality educational tools.',
    },
    {
        question: 'Can I use the animations in my content?',
        answer: 'Absolutely. All animations you generate are yours to use however you like—in YouTube videos, presentations, courses, or any other educational content.',
    },
    {
        question: 'How long does it take to generate an animation?',
        answer: 'Most animations are generated in under 60 seconds. Complex topics with multiple scenes may take a bit longer, but you\'ll see progress updates in real-time.',
    },
];

export default function FAQ() {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return (
        <section className="relative section-spacing bg-slate-950 overflow-hidden">
            {/* ChromaGrid Background */}
            <div className="absolute inset-0 opacity-20">
                <ChromaGrid
                    cellSize={80}
                    gap={8}
                    colors={['#8b5cf6', '#6366f1', '#4f46e5', '#7c3aed']}
                    speed={1}
                />
            </div>

            <div className="relative z-10 max-w-3xl mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-semibold text-white mb-4">
                        Frequently asked questions
                    </h2>
                    <p className="text-gray-400">
                        Everything you need to know about Nimator
                    </p>
                </div>

                {/* FAQ Accordion */}
                <div className="space-y-4">
                    {FAQS.map((faq, index) => (
                        <div
                            key={index}
                            className="border border-white/5 rounded-xl overflow-hidden bg-slate-900/80 backdrop-blur-sm"
                        >
                            <button
                                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                                className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-slate-800/50 transition-colors"
                            >
                                <span className="text-white font-medium pr-4">
                                    {faq.question}
                                </span>
                                <motion.div
                                    animate={{ rotate: openIndex === index ? 180 : 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="text-gray-400 flex-shrink-0"
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
                                        <p className="px-6 pb-5 text-gray-400 leading-relaxed">
                                            {faq.answer}
                                        </p>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
