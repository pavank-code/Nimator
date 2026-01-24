import React from 'react';
import Link from 'next/link';

const FOOTER_LINKS = [
    { label: 'AI Tutor', href: '/tutor' },
    { label: 'Generate Video', href: '/app' },
    { label: 'About', href: '#philosophy' },
    { label: 'Docs', href: '#' },
    { label: 'GitHub', href: 'https://github.com' },
    { label: 'Contact', href: '#' },
];

export default function Footer() {
    return (
        <footer className="py-16 bg-slate-950 border-t border-white/5">
            <div className="max-w-6xl mx-auto px-6">
                {/* Trust Signal */}
                <p className="text-center text-gray-500 text-sm mb-10">
                    Built by people who love math, design, and clarity.
                </p>

                <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                    {/* Logo & Copyright */}
                    <div className="flex items-center gap-3">
                        <img
                            src="/logo_128.png"
                            alt="Nimator"
                            className="h-6 w-6"
                        />
                        <span className="text-white font-medium">Nimator</span>
                        <span className="text-gray-600">·</span>
                        <span className="text-gray-500 text-sm">
                            © 2026. All rights reserved.
                        </span>
                    </div>

                    {/* Links */}
                    <nav className="flex items-center gap-8">
                        {FOOTER_LINKS.map((link) => (
                            <Link
                                key={link.label}
                                href={link.href}
                                className="text-gray-500 text-sm hover:text-white transition-colors duration-200"
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>
                </div>
            </div>
        </footer>
    );
}
