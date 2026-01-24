'use client';

import React, { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    isStreaming?: boolean;
}

interface ChatMessageProps {
    message: Message;
}

function renderLatex(text: string): string {
    // Render display math $$...$$
    text = text.replace(/\$\$([^$]+)\$\$/g, (_, latex) => {
        try {
            return `<div class="katex-display my-4">${katex.renderToString(latex, { displayMode: true, throwOnError: false })}</div>`;
        } catch {
            return `<code>${latex}</code>`;
        }
    });

    // Render inline math $...$
    text = text.replace(/\$([^$\n]+)\$/g, (_, latex) => {
        try {
            return katex.renderToString(latex, { displayMode: false, throwOnError: false });
        } catch {
            return `<code>${latex}</code>`;
        }
    });

    return text;
}

function renderMarkdown(text: string): string {
    // First render LaTeX
    text = renderLatex(text);

    // Code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre class="bg-[#1a1a1a] rounded-lg p-4 my-3 overflow-x-auto"><code class="text-sm text-gray-300">${escapeHtml(code.trim())}</code></pre>`;
    });

    // Headers
    text = text.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
    text = text.replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-5 mb-3">$1</h2>');
    text = text.replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-6 mb-4">$1</h1>');

    // Bold and italic
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold">$1</strong>');
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code class="bg-[#3a3a3a] px-1.5 py-0.5 rounded text-sm text-pink-400">$1</code>');

    // Lists
    text = text.replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>');
    text = text.replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 list-decimal">$2</li>');

    // Wrap consecutive list items
    text = text.replace(/(<li[^>]*>.*<\/li>\n?)+/g, '<ul class="my-2">$&</ul>');

    // Paragraphs (lines with content)
    text = text.replace(/^([^<\n].+)$/gm, '<p class="my-2">$1</p>');

    // Clean up empty paragraphs
    text = text.replace(/<p class="my-2"><\/p>/g, '');

    // Line breaks
    text = text.replace(/\n\n/g, '<br/>');

    return text;
}

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

export default function ChatMessage({ message }: ChatMessageProps) {
    const contentRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Re-render when content changes
        if (contentRef.current && message.content) {
            contentRef.current.innerHTML = renderMarkdown(message.content);
        }
    }, [message.content]);

    const isUser = message.role === 'user';

    return (
        <div className={`py-6 ${isUser ? '' : 'bg-[#2a2a2a] -mx-4 px-4 rounded-lg'}`}>
            <div className="flex gap-4">
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-blue-600' : 'bg-gradient-to-br from-teal-400 to-blue-500'
                    }`}>
                    {isUser ? (
                        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                        </svg>
                    ) : (
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                    )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm text-gray-400 mb-1">
                        {isUser ? 'You' : 'AI Tutor'}
                    </div>

                    {message.isStreaming ? (
                        <div className="flex items-center gap-2 text-gray-400">
                            <div className="flex gap-1">
                                {[0, 1, 2].map(i => (
                                    <div
                                        key={i}
                                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                                        style={{ animationDelay: `${i * 150}ms` }}
                                    />
                                ))}
                            </div>
                            <span className="text-sm">Thinking...</span>
                        </div>
                    ) : (
                        <div
                            ref={contentRef}
                            className="prose prose-invert max-w-none text-gray-100 leading-relaxed"
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
