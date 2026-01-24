'use client';

import React, { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { cn } from '../../lib/utils';

interface BlurTextProps {
    text: string;
    delay?: number;
    duration?: number;
    className?: string;
    animateBy?: 'words' | 'characters';
    direction?: 'top' | 'bottom';
    onAnimationComplete?: () => void;
    as?: 'span' | 'div';
}

export default function BlurText({
    text,
    delay = 0,
    duration = 0.8,
    className,
    animateBy = 'words',
    direction = 'bottom',
    onAnimationComplete,
    as = 'span',
}: BlurTextProps) {
    const containerRef = useRef<HTMLElement>(null);
    const hasAnimated = useRef(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!containerRef.current || hasAnimated.current || !mounted) return;

        const elements = containerRef.current.querySelectorAll('.blur-text-element');

        gsap.set(elements, {
            opacity: 0,
            filter: 'blur(12px)',
            y: direction === 'bottom' ? 30 : -30,
        });

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting && !hasAnimated.current) {
                        hasAnimated.current = true;

                        gsap.to(elements, {
                            opacity: 1,
                            filter: 'blur(0px)',
                            y: 0,
                            duration: duration,
                            stagger: 0.08,
                            delay: delay,
                            ease: 'power3.out',
                            onComplete: onAnimationComplete,
                        });
                    }
                });
            },
            { threshold: 0.2 }
        );

        observer.observe(containerRef.current);

        return () => observer.disconnect();
    }, [delay, duration, direction, onAnimationComplete, mounted]);

    const splitText = () => {
        if (animateBy === 'characters') {
            return text.split('').map((char, index) => (
                <span
                    key={index}
                    className="blur-text-element inline-block"
                    style={{ whiteSpace: char === ' ' ? 'pre' : 'normal' }}
                >
                    {char === ' ' ? '\u00A0' : char}
                </span>
            ));
        }

        return text.split(' ').map((word, index) => (
            <span key={index} className="blur-text-element inline-block mr-[0.25em]">
                {word}
            </span>
        ));
    };

    const Component = as;

    // Return plain text on server, animated on client
    if (!mounted) {
        return (
            <Component className={cn('inline-block', className)}>
                {text}
            </Component>
        );
    }

    return (
        <Component ref={containerRef as any} className={cn('inline-block', className)}>
            {splitText()}
        </Component>
    );
}
