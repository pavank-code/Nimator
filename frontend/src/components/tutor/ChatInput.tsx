'use client';

import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';

export interface ChatInputHandle {
    toggleListening: () => void;
    clear: () => void;
}

interface ChatInputProps {
    onSendMessage: (message: string) => void;
    isLoading: boolean;
    onListeningChange: (isListening: boolean) => void;
}

const ChatInput = forwardRef<ChatInputHandle, ChatInputProps>(({ onSendMessage, isLoading, onListeningChange }, ref) => {
    const [value, setValue] = useState('');
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef<any>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useImperativeHandle(ref, () => ({
        toggleListening: () => {
            if (!recognitionRef.current) return;
            if (isListening) {
                recognitionRef.current.stop();
            } else {
                recognitionRef.current.start();
                setIsListening(true);
            }
        },
        clear: () => setValue('')
    }));

    useEffect(() => {
        onListeningChange(isListening);
    }, [isListening, onListeningChange]);

    useEffect(() => {
        if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onresult = (event: any) => {
                const transcript = Array.from(event.results)
                    .map((result: any) => result[0].transcript)
                    .join('');
                setValue(transcript);
            };

            recognitionRef.current.onend = () => setIsListening(false);
            recognitionRef.current.onerror = () => setIsListening(false);
        }
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (value.trim() && !isLoading) {
                onSendMessage(value);
                setValue('');
            }
        }
    };

    const toggleListeningInternal = () => {
        if (!recognitionRef.current) return;
        if (isListening) {
            recognitionRef.current.stop();
        } else {
            recognitionRef.current.start();
            setIsListening(true);
        }
    };

    return (
        <div className="p-4 border-t border-white/10 bg-[#171717]">
            <div className="max-w-3xl mx-auto">
                <div className="relative flex items-end bg-[#2f2f2f] rounded-2xl border border-white/10 shadow-lg">
                    <textarea
                        ref={textareaRef}
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about math, physics, algorithms, or ML..."
                        rows={1}
                        className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none p-4 pr-24 max-h-48 min-h-[56px]"
                        style={{ height: 'auto' }}
                        disabled={isLoading}
                    />

                    <div className="absolute right-2 bottom-2 flex items-center gap-1">
                        {/* Voice Button */}
                        <button
                            onClick={toggleListeningInternal}
                            className={`p-2 rounded-lg transition ${isListening ? 'bg-red-500 text-white animate-pulse' : 'text-gray-400 hover:text-white hover:bg-white/10'}`}
                            title={isListening ? 'Stop listening' : 'Voice input'}
                        >
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                            </svg>
                        </button>

                        {/* Send Button */}
                        <button
                            onClick={() => {
                                if (value.trim() && !isLoading) {
                                    onSendMessage(value);
                                    setValue('');
                                }
                            }}
                            disabled={!value.trim() || isLoading}
                            className={`p-2 rounded-lg transition ${value.trim() && !isLoading ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-400 hover:to-blue-400' : 'text-gray-600 cursor-not-allowed'}`}
                            title="Send message"
                        >
                            {isLoading ? (
                                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                <div className="flex items-center justify-between mt-2">
                    <p className="text-xs text-gray-500">
                        Press Enter to send • Shift+Enter for new line
                    </p>
                    <p className="text-xs text-gray-500">
                        AI Tutor can make mistakes. Verify important information.
                    </p>
                </div>
            </div>
        </div>
    );
});

ChatInput.displayName = 'ChatInput';

export default ChatInput;
