'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import ChatMessage from '../../components/tutor/ChatMessage';
import VideoPanel from '../../components/tutor/VideoPanel';
import VoiceOrb from '../../components/tutor/VoiceOrb';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

export default function TutorPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentVideo, setCurrentVideo] = useState<VideoData | null>(null);
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [showSidebar, setShowSidebar] = useState(false);

    const [videoHistory, setVideoHistory] = useState<VideoData[]>([]);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const recognitionRef = useRef<any>(null);
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

$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$

**Try asking:** "Explain gradient descent with a visual"`,
            timestamp: new Date()
        }]);
    }, []);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Speech recognition setup
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
                setInputValue(transcript);
            };

            recognitionRef.current.onend = () => setIsListening(false);
            recognitionRef.current.onerror = () => setIsListening(false);
        }
    }, []);

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
        setInputValue('');
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
    }, [isLoading, sessionId]);

    const speakText = async (text: string) => {
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
    };

    const triggerVideoGeneration = async (prompt: string, voiceoverText: string) => {
        // Create initial video object with a temp ID to track it before we get the real job_id
        const tempId = generateId();
        const newVideo: VideoData = {
            job_id: tempId,
            status: 'starting',
            progress: 0,
            prompt,
            voiceover_text: voiceoverText
        };

        // Add to history and set as current
        setVideoHistory(prev => [newVideo, ...prev]);
        setCurrentVideo(newVideo);
        setShowSidebar(true);

        try {
            const response = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, duration_seconds: 90, sample_mode: true })
            });

            if (!response.ok) throw new Error('Failed');

            const { job_id } = await response.json();

            // Helper to update video properties
            const updateWithJobId = (v: VideoData) => ({ ...v, job_id, status: 'processing' });

            // Update the temp video with the real job_id
            setVideoHistory(prev => prev.map(v => v.job_id === tempId ? updateWithJobId(v) : v));
            setCurrentVideo(prev => (prev?.job_id === tempId) ? updateWithJobId(prev) : prev);

            const poll = setInterval(async () => {
                try {
                    const res = await fetch(`${API_URL}/api/status/${job_id}`);
                    const data = await res.json();

                    // Update logic
                    const updateStatus = (v: VideoData) => ({
                        ...v,
                        status: data.status,
                        progress: data.progress || 0,
                        video_url: data.video_url
                    });

                    // Update in history using the REAL job_id
                    setVideoHistory(prev => prev.map(v => v.job_id === job_id ? updateStatus(v) : v));

                    // Update current if it matches
                    setCurrentVideo(prev => (prev && prev.job_id === job_id) ? updateStatus(prev) : prev);

                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(poll);
                        if (data.status === 'completed' && voiceoverText) {
                            speakText(voiceoverText);
                        }
                    }
                } catch { }
            }, 2000);

            // Timeout after 10 minutes
            setTimeout(() => clearInterval(poll), 600000);
        } catch {
            const markFailed = (v: VideoData) => ({ ...v, status: 'failed' });
            setVideoHistory(prev => prev.map(v => v.job_id === tempId ? markFailed(v) : v));
            setCurrentVideo(prev => (prev?.job_id === tempId) ? markFailed(prev) : prev);
        }
    };

    const toggleListening = () => {
        if (!recognitionRef.current) return;
        if (isListening) {
            recognitionRef.current.stop();
        } else {
            recognitionRef.current.start();
            setIsListening(true);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputValue);
        }
    };

    return (
        <div className="flex h-screen bg-[#212121] text-white">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="flex items-center justify-between h-14 px-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <button onClick={() => router.push('/')} className="p-2 hover:bg-white/10 rounded-lg">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>
                        <h1 className="text-lg font-semibold">AI Tutor</h1>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowSidebar(!showSidebar)}
                            className={`p-2 rounded-lg transition ${showSidebar ? 'bg-white/10' : 'hover:bg-white/10'}`}
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
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Voice Orb */}
                <VoiceOrb
                    isListening={isListening}
                    isSpeaking={isSpeaking}
                    onToggle={toggleListening}
                />

                {/* Input Area - ChatGPT Style */}
                <div className="p-4 border-t border-white/10">
                    <div className="max-w-3xl mx-auto">
                        <div className="relative flex items-end bg-[#2f2f2f] rounded-2xl border border-white/10">
                            <textarea
                                ref={inputRef}
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Message AI Tutor..."
                                rows={1}
                                className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none p-4 pr-24 max-h-48 min-h-[56px]"
                                style={{ height: 'auto' }}
                                disabled={isLoading}
                            />

                            <div className="absolute right-2 bottom-2 flex items-center gap-1">
                                {/* Voice Button */}
                                <button
                                    onClick={toggleListening}
                                    className={`p-2 rounded-lg transition ${isListening ? 'bg-red-500 text-white' : 'text-gray-400 hover:text-white hover:bg-white/10'}`}
                                >
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                                        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                                    </svg>
                                </button>

                                {/* Send Button */}
                                <button
                                    onClick={() => sendMessage(inputValue)}
                                    disabled={!inputValue.trim() || isLoading}
                                    className={`p-2 rounded-lg transition ${inputValue.trim() && !isLoading ? 'bg-white text-black hover:bg-gray-200' : 'text-gray-600 cursor-not-allowed'}`}
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <p className="text-xs text-gray-500 text-center mt-2">
                            AI Tutor can make mistakes. Verify important information.
                        </p>
                    </div>
                </div>
            </div>

            {/* Video Sidebar */}
            {showSidebar && (
                <VideoPanel
                    video={currentVideo}
                    history={videoHistory}
                    onSelectVideo={setCurrentVideo}
                    isSpeaking={isSpeaking}
                    onClose={() => setShowSidebar(false)}
                    onClear={() => setCurrentVideo(null)}
                />
            )}
        </div>
    );
}
