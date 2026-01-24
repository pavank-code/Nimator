'use client';

import React, { useRef, useEffect } from 'react';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface ChatPanelProps {
    messages: Message[];
    inputValue: string;
    isLoading: boolean;
    isListening: boolean;
    onInputChange: (value: string) => void;
    onSend: () => void;
    onToggleListen: () => void;
    onKeyDown: (e: React.KeyboardEvent) => void;
}

// Simple markdown renderer
function renderMarkdown(text: string): React.ReactNode {
    // Split into lines and process
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    let inCodeBlock = false;
    let codeContent = '';
    let codeLanguage = '';

    lines.forEach((line, index) => {
        // Code block handling
        if (line.startsWith('```')) {
            if (!inCodeBlock) {
                inCodeBlock = true;
                codeLanguage = line.slice(3).trim();
                codeContent = '';
            } else {
                elements.push(
                    <pre key={`code-${index}`} className="bg-gray-900 rounded-lg p-4 my-2 overflow-x-auto">
                        <code className="text-sm text-gray-300">{codeContent}</code>
                    </pre>
                );
                inCodeBlock = false;
            }
            return;
        }

        if (inCodeBlock) {
            codeContent += (codeContent ? '\n' : '') + line;
            return;
        }

        // Headers
        if (line.startsWith('### ')) {
            elements.push(<h3 key={index} className="text-lg font-semibold text-white mt-3 mb-2">{line.slice(4)}</h3>);
            return;
        }
        if (line.startsWith('## ')) {
            elements.push(<h2 key={index} className="text-xl font-bold text-white mt-4 mb-2">{line.slice(3)}</h2>);
            return;
        }
        if (line.startsWith('# ')) {
            elements.push(<h1 key={index} className="text-2xl font-bold text-white mt-4 mb-3">{line.slice(2)}</h1>);
            return;
        }

        // Bullet points
        if (line.startsWith('- ') || line.startsWith('* ')) {
            elements.push(
                <li key={index} className="ml-4 text-gray-300 list-disc">
                    {processInlineMarkdown(line.slice(2))}
                </li>
            );
            return;
        }

        // Numbered lists
        const numberedMatch = line.match(/^(\d+)\.\s(.*)$/);
        if (numberedMatch) {
            elements.push(
                <li key={index} className="ml-4 text-gray-300 list-decimal">
                    {processInlineMarkdown(numberedMatch[2])}
                </li>
            );
            return;
        }

        // Empty line
        if (!line.trim()) {
            elements.push(<br key={index} />);
            return;
        }

        // Regular paragraph
        elements.push(
            <p key={index} className="text-gray-300 my-1">
                {processInlineMarkdown(line)}
            </p>
        );
    });

    return elements;
}

function processInlineMarkdown(text: string): React.ReactNode {
    // Process inline code, bold, italic, and links
    const parts: React.ReactNode[] = [];
    let remaining = text;
    let keyIndex = 0;

    // Process inline code
    const codeRegex = /`([^`]+)`/g;
    let lastIndex = 0;
    let match;

    while ((match = codeRegex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            parts.push(processBoldItalic(text.slice(lastIndex, match.index), keyIndex++));
        }
        parts.push(
            <code key={`inline-${keyIndex++}`} className="bg-gray-700 px-1.5 py-0.5 rounded text-sm text-pink-400">
                {match[1]}
            </code>
        );
        lastIndex = match.index + match[0].length;
    }

    if (lastIndex < text.length) {
        parts.push(processBoldItalic(text.slice(lastIndex), keyIndex));
    }

    return parts.length > 0 ? parts : processBoldItalic(text, 0);
}

function processBoldItalic(text: string, key: number): React.ReactNode {
    // Bold: **text**
    const boldRegex = /\*\*([^*]+)\*\*/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            parts.push(<span key={`text-${key}-${lastIndex}`}>{text.slice(lastIndex, match.index)}</span>);
        }
        parts.push(<strong key={`bold-${key}-${match.index}`} className="font-semibold text-white">{match[1]}</strong>);
        lastIndex = match.index + match[0].length;
    }

    if (lastIndex < text.length) {
        parts.push(<span key={`text-${key}-end`}>{text.slice(lastIndex)}</span>);
    }

    return parts.length > 0 ? parts : text;
}

export default function ChatPanel({
    messages,
    inputValue,
    isLoading,
    isListening,
    onInputChange,
    onSend,
    onToggleListen,
    onKeyDown
}: ChatPanelProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="w-1/2 flex flex-col border-r border-gray-700/50">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-700/70 text-gray-100'
                                }`}
                        >
                            {message.role === 'assistant' ? (
                                <div className="prose prose-invert prose-sm max-w-none">
                                    {renderMarkdown(message.content)}
                                </div>
                            ) : (
                                <p>{message.content}</p>
                            )}
                            <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                                }`}>
                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700/70 rounded-2xl px-4 py-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-700/50">
                <div className="flex items-end gap-2 bg-gray-800 rounded-xl p-2">
                    {/* Microphone Button */}
                    <button
                        onClick={onToggleListen}
                        className={`p-3 rounded-lg transition-all ${isListening
                                ? 'bg-blue-600 text-white animate-pulse'
                                : 'bg-gray-700 text-gray-400 hover:text-white hover:bg-gray-600'
                            }`}
                        title={isListening ? 'Stop listening' : 'Start voice input'}
                    >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                        </svg>
                    </button>

                    {/* Text Input */}
                    <textarea
                        value={inputValue}
                        onChange={(e) => onInputChange(e.target.value)}
                        onKeyDown={onKeyDown}
                        placeholder="Ask me anything..."
                        className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none p-2 max-h-32"
                        rows={1}
                        disabled={isLoading}
                    />

                    {/* Send Button */}
                    <button
                        onClick={onSend}
                        disabled={!inputValue.trim() || isLoading}
                        className={`p-3 rounded-lg transition-all ${inputValue.trim() && !isLoading
                                ? 'bg-blue-600 text-white hover:bg-blue-500'
                                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            }`}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </div>

                <p className="text-xs text-gray-500 mt-2 text-center">
                    Press Enter to send • Shift+Enter for new line
                </p>
            </div>
        </div>
    );
}
