'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ChatMessage from '../../components/tutor/ChatMessage';
import VideoPanel from '../../components/tutor/VideoPanel';
import VoiceOrb from '../../components/tutor/VoiceOrb';
import ChatInput, { ChatInputHandle } from '../../components/tutor/ChatInput';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Example prompts for users
const EXAMPLE_PROMPTS = [
    { icon: '📐', text: 'Explain the Pythagorean theorem visually' },
    { icon: '📉', text: 'Show me how gradient descent works' },
    { icon: '🔢', text: 'Visualize matrix multiplication' },
    { icon: '🌀', text: 'Explain derivatives with an animation' },
    { icon: '🔍', text: 'Show binary search algorithm' },
    { icon: '📊', text: 'Explain eigenvectors visually' },
];

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    isStreaming?: boolean;
}

interface VideoData {
    job_id: string;
    status: string;
    progress: number;
    video_url?: string;
    prompt?: string;
    voiceover_text?: string;
}

interface VisualObject {
    object_id: string;
    object_type: string;
    display_name: string;
    color: string;
}

export default function TutorPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([]);
    // inputValue state moved to ChatInput
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentVideo, setCurrentVideo] = useState<VideoData | null>(null);
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [showSidebar, setShowSidebar] = useState(true);
    const [visualObjects, setVisualObjects] = useState<VisualObject[]>([]);
    const [showExamples, setShowExamples] = useState(true);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const chatInputRef = useRef<ChatInputHandle>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Welcome message
    useEffect(() => {
        setMessages([{
            id: '1',
            role: 'assistant',
            content: `# Welcome to AI Tutor! 🎓

I'm your personal tutor for **mathematics**, **physics**, **algorithms**, and **machine learning**.

I can help you with:
- Explaining concepts with **LaTeX equations**: $E = mc^2$
- Creating **visual animations** to illustrate ideas
- Step-by-step problem solving

$$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$

**Try asking:** "Explain gradient descent with a visual" or click one of the example prompts below!`,
            timestamp: new Date()
        }]);
    }, []);

    // Hide examples after first message
    useEffect(() => {
        if (messages.length > 1) {
            setShowExamples(false);
        }
    }, [messages]);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const speakText = useCallback(async (text: string) => {
        setIsSpeaking(true);
        try {
            const response = await fetch(`${API_URL}/api/tutor/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text.slice(0, 500), voice: 'aura-asteria-en' })
            });

            if (response.ok) {
                const blob = await response.blob();
                const audio = new Audio(URL.createObjectURL(blob));
                audioRef.current = audio;
                audio.onended = () => setIsSpeaking(false);
                await audio.play();
            } else {
                setIsSpeaking(false);
            }
        } catch {
            setIsSpeaking(false);
        }
    }, []);

    const triggerVideoGeneration = useCallback(async (prompt: string, voiceoverText: string) => {
        setCurrentVideo({ job_id: '', status: 'starting', progress: 0, prompt, voiceover_text: voiceoverText });
        setShowSidebar(true);

        try {
            const response = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, duration_seconds: 60, sample_mode: true })
            });

            if (!response.ok) throw new Error('Failed');

            const { job_id } = await response.json();
            setCurrentVideo(prev => prev ? { ...prev, job_id, status: 'processing' } : null);

            const poll = setInterval(async () => {
                try {
                    const res = await fetch(`${API_URL}/api/status/${job_id}`);
                    const data = await res.json();

                    setCurrentVideo(prev => prev ? {
                        ...prev,
                        status: data.status,
                        progress: data.progress || 0,
                        video_url: data.video_url
                    } : null);

                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(poll);
                        if (data.status === 'completed' && voiceoverText) {
                            speakText(voiceoverText);
                        }
                    }
                } catch { }
            }, 2000);

            setTimeout(() => clearInterval(poll), 600000);
        } catch {
            setCurrentVideo(null);
        }
    }, [speakText]);

    const generateId = () => Math.random().toString(36).substr(2, 9);

    const sendMessage = useCallback(async (text: string) => {
        if (!text.trim() || isLoading) return;

        const userMsg: Message = {
            id: generateId(),
            role: 'user',
            content: text.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        chatInputRef.current?.clear();
        setIsLoading(true);

        // Add placeholder for assistant
        const assistantId = generateId();
        setMessages(prev => [...prev, {
            id: assistantId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            isStreaming: true
        }]);

        try {
            const response = await fetch(`${API_URL}/api/tutor/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text.trim(), session_id: sessionId })
            });

            if (!response.ok) throw new Error('Failed');

            const data = await response.json();
            setSessionId(data.session_id);

            // Update assistant message
            setMessages(prev => prev.map(m =>
                m.id === assistantId
                    ? { ...m, content: data.response, isStreaming: false }
                    : m
            ));

            // Update visual objects if available
            if (data.visual_objects) {
                setVisualObjects(data.visual_objects);
            }

            // Handle video generation
            if (data.should_generate_video && data.video_prompt) {
                triggerVideoGeneration(data.video_prompt, data.response);
            } else if (data.response) {
                // Speak non-video responses
                speakText(data.response);
            }

        } catch (error) {
            setMessages(prev => prev.map(m =>
                m.id === assistantId
                    ? { ...m, content: "I'm having trouble connecting. Please try again.", isStreaming: false }
                    : m
            ));
        } finally {
            setIsLoading(false);
        }
    }, [isLoading, sessionId, speakText, triggerVideoGeneration]);

    return (
        <div className="flex h-screen bg-[#212121] text-white">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="flex items-center justify-between h-14 px-4 border-b border-white/10 bg-[#171717]">
                    <div className="flex items-center gap-3">
                        <button onClick={() => router.push('/')} className="p-2 hover:bg-white/10 rounded-lg transition">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>
                        <div className="flex items-center gap-2">
                            <span className="text-xl">🎓</span>
                            <h1 className="text-lg font-semibold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">AI Tutor</h1>
                        </div>
                        {sessionId && (
                            <span className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded">
                                Session active
                            </span>
                        )}
                    </div>

                    <div className="flex items-center gap-2">
                        {/* New Chat Button */}
                        <button
                            onClick={() => {
                                setMessages([{
                                    id: '1',
                                    role: 'assistant',
                                    content: `# Welcome back! 🎓\n\nI'm ready to help you learn. What would you like to explore today?`,
                                    timestamp: new Date()
                                }]);
                                setSessionId(null);
                                setCurrentVideo(null);
                                setVisualObjects([]);
                                setShowExamples(true);
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm hover:bg-white/10 rounded-lg transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            New Chat
                        </button>

                        {/* Video App Link */}
                        <Link
                            href="/app"
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm hover:bg-white/10 rounded-lg transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            Video Generator
                        </Link>

                        {/* Toggle Sidebar */}
                        <button
                            onClick={() => setShowSidebar(!showSidebar)}
                            className={`p-2 rounded-lg transition ${showSidebar ? 'bg-white/10' : 'hover:bg-white/10'}`}
                            title={showSidebar ? 'Hide video panel' : 'Show video panel'}
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                            </svg>
                        </button>
                    </div>
                </header>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto">
                    <div className="max-w-3xl mx-auto py-6 px-4">
                        {messages.map(message => (
                            <ChatMessage key={message.id} message={message} />
                        ))}
                        
                        {/* Example Prompts - shown only at start */}
                        {showExamples && messages.length <= 1 && (
                            <div className="mt-6 mb-4">
                                <p className="text-sm text-gray-400 mb-3">Try one of these:</p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    {EXAMPLE_PROMPTS.map((prompt, index) => (
                                        <button
                                            key={index}
                                            onClick={() => sendMessage(prompt.text)}
                                            className="flex items-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-left text-sm transition group"
                                        >
                                            <span className="text-lg">{prompt.icon}</span>
                                            <span className="text-gray-300 group-hover:text-white">{prompt.text}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Visual Objects Display */}
                        {visualObjects.length > 0 && (
                            <div className="mt-4 p-3 bg-white/5 rounded-xl border border-white/10">
                                <p className="text-xs text-gray-400 mb-2">Currently on screen:</p>
                                <div className="flex flex-wrap gap-2">
                                    {visualObjects.map((obj) => (
                                        <span
                                            key={obj.object_id}
                                            className="inline-flex items-center gap-1 px-2 py-1 bg-white/10 rounded text-xs"
                                            style={{ borderLeft: `3px solid ${obj.color}` }}
                                        >
                                            {obj.display_name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Voice Orb */}
                <VoiceOrb
                    isListening={isListening}
                    isSpeaking={isSpeaking}
                    onToggle={() => chatInputRef.current?.toggleListening()}
                />

                {/* Input Area - ChatGPT Style */}
                <ChatInput
                    ref={chatInputRef}
                    onSendMessage={sendMessage}
                    isLoading={isLoading}
                    onListeningChange={setIsListening}
                />
            </div>

            {/* Video Sidebar */}
            {showSidebar && (
                <VideoPanel
                    video={currentVideo}
                    isSpeaking={isSpeaking}
                    onClose={() => setShowSidebar(false)}
                    onClear={() => setCurrentVideo(null)}
                />
            )}
        </div>
    );
}
