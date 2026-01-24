import type { Metadata } from 'next';
import Script from 'next/script';

export const metadata: Metadata = {
    title: 'AI Tutor | Visual Explainer',
    description: 'Interactive AI tutor with visual explanations and LaTeX support',
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
            {children}
        </>
    );
}
