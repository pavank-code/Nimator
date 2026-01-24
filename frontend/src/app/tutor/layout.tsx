import type { Metadata } from 'next';
import Script from 'next/script';

export const metadata: Metadata = {
    title: 'AI Tutor - Interactive Math & Science Learning | Nimator',
    description: 'Learn mathematics, physics, algorithms, and machine learning with an AI-powered tutor. Get visual explanations, LaTeX equations, and animated videos to understand complex concepts.',
    keywords: ['AI tutor', 'math tutor', 'visual learning', 'LaTeX', 'animations', 'gradient descent', 'machine learning', 'physics'],
    openGraph: {
        title: 'AI Tutor - Learn with Visual Animations',
        description: 'Interactive AI tutor with visual explanations and LaTeX support for mathematics, physics, and computer science.',
        type: 'website',
    },
};

export default function TutorLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            {/* KaTeX for LaTeX rendering */}
            <link
                rel="stylesheet"
                href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"
                crossOrigin="anonymous"
            />
            <Script
                src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"
                crossOrigin="anonymous"
                strategy="beforeInteractive"
            />
            <Script
                src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
                crossOrigin="anonymous"
                strategy="afterInteractive"
            />
            {children}
        </>
    );
}
