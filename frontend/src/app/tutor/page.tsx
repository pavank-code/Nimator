'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import VoiceNotch from '../../components/tutor/VoiceNotch';
import ChatPanel from '../../components/tutor/ChatPanel';
import ContentPanel from '../../components/tutor/ContentPanel';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface VideoData {
    job_id: string;
    status: string;
    progress: number;
    video_url?: string;
    prompt?: string;
    voiceover_text?: string; // Text to speak in sync with video
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
    const [voiceEnabled, setVoiceEnabled] = useState(true);

    // Refs for sync playback
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const recognitionRef = useRef<any>(null);

    // Initialize with welcome message
    useEffect(() => {
        setMessages([{
            role: 'assistant',
            content: "Hello! I'm your AI tutor. Ask me anything about **mathematics**, **physics**, **algorithms**, or **machine learning**. I can also generate visual explanations when helpful! 🎓\n\nTry asking:\n- \"Explain gradient descent visually\"\n- \"How does the Pythagorean theorem work?\"\n- \"Show me how binary search works\"",
            timestamp: new Date()
        }]);
    }, []);

    // Initialize speech recognition
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

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };

            recognitionRef.current.onerror = () => {
                setIsListening(false);
            };
        }
    }, []);

    const sendMessage = useCallback(async (messageText: string) => {
        if (!messageText.trim() || isLoading) return;

        const userMessage: Message = {
            role: 'user',
            content: messageText.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            // Send to tutor API
            const response = await fetch(`${API_URL}/api/tutor/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText.trim(),
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            setSessionId(data.session_id);

            // Step 1: Add assistant message immediately (text displays first)
            const assistantMessage: Message = {
                role: 'assistant',
                content: data.response,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, assistantMessage]);

            // Step 2: Handle video generation (starts in parallel)
            if (data.should_generate_video && data.video_prompt) {
                // Start video generation - voice will sync when video is ready
                await triggerVideoGeneration(
                    data.video_prompt,
                    data.modify_video,
                    data.modifications,
                    data.response // Pass the response text for voiceover sync
                );
            } else {
                // No video - just speak the response normally
                if (voiceEnabled) {
                    speakText(data.response);
                }
            }

        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm having trouble connecting. Please try again in a moment.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    }, [isLoading, sessionId, voiceEnabled]);

    // Speak text without video (for regular responses)
    const speakText = async (text: string) => {
        const cleanText = text
            .replace(/[#*_`]/g, '')
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
            .replace(/\n+/g, '. ')
            .slice(0, 500);

        setIsSpeaking(true);

        try {
            const response = await fetch(`${API_URL}/api/tutor/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: cleanText, voice: 'aura-asteria-en' })
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.onended = () => setIsSpeaking(false);
                audio.onerror = () => setIsSpeaking(false);
                await audio.play();
            } else {
                fallbackBrowserTTS(cleanText);
            }
        } catch (error) {
            fallbackBrowserTTS(cleanText);
        }
    };

    const fallbackBrowserTTS = (text: string) => {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.onend = () => setIsSpeaking(false);
            window.speechSynthesis.speak(utterance);
        } else {
            setIsSpeaking(false);
        }
    };

    // Play video and voice in sync
    const playVideoWithVoice = async (videoUrl: string, voiceoverText: string) => {
        if (!voiceEnabled) {
            // Just play video without voice
            return;
        }

        setIsSpeaking(true);

        try {
            // Pre-fetch the audio
            const response = await fetch(`${API_URL}/api/tutor/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: voiceoverText.replace(/[#*_`]/g, '').replace(/\n+/g, '. ').slice(0, 1000),
                    voice: 'aura-asteria-en'
                })
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);

                // Create audio element for sync
                const audio = new Audio(audioUrl);
                audioRef.current = audio;

                audio.onended = () => {
                    setIsSpeaking(false);
                };

                // Play audio (video will be controlled by ContentPanel)
                await audio.play();
            } else {
                fallbackBrowserTTS(voiceoverText);
            }
        } catch (error) {
            console.error('Voice sync error:', error);
            setIsSpeaking(false);
        }
    };

    const triggerVideoGeneration = async (
        prompt: string,
        isModify: boolean,
        modifications?: any,
        voiceoverText?: string
    ) => {
        setCurrentVideo({
            job_id: '',
            status: 'starting',
            progress: 0,
            prompt,
            voiceover_text: voiceoverText
        });

        try {
            let finalPrompt = prompt;
            if (isModify && modifications) {
                const modStr = Object.entries(modifications)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(', ');
                finalPrompt = `${prompt} (with modifications: ${modStr})`;
            }

            const response = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: finalPrompt,
                    duration_seconds: 60,
                    sample_mode: true
                })
            });

            if (!response.ok) throw new Error('Failed to start generation');

            const { job_id } = await response.json();
            setCurrentVideo(prev => prev ? {
                ...prev,
                job_id,
                status: 'processing'
            } : null);

            // Poll for status
            const pollInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(`${API_URL}/api/status/${job_id}`);
                    const statusData = await statusRes.json();

                    const isCompleted = statusData.status === 'completed';
                    const isFailed = statusData.status === 'failed';

                    setCurrentVideo(prev => prev ? {
                        ...prev,
                        status: statusData.status,
                        progress: statusData.progress || 0,
                        video_url: statusData.video_url
                    } : null);

                    if (isCompleted || isFailed) {
                        clearInterval(pollInterval);

                        // Step 4: When video is ready, trigger sync playback
                        if (isCompleted && statusData.video_url && voiceoverText && voiceEnabled) {
                            playVideoWithVoice(statusData.video_url, voiceoverText);
                        }
                    }
                } catch (e) {
                    console.error('Poll error:', e);
                }
            }, 2000);

            setTimeout(() => clearInterval(pollInterval), 300000);

        } catch (error) {
            console.error('Video generation error:', error);
            setCurrentVideo(null);
        }
    };

    const toggleListening = () => {
        if (!recognitionRef.current) {
            alert('Voice input is not supported in this browser.');
            return;
        }

        if (isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
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

    // Handler for when video starts playing (called from ContentPanel)
    const onVideoPlay = () => {
        // Audio is already playing from playVideoWithVoice
    };

    // Handler to stop voice when video is cleared
    const handleClearVideo = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }
        setIsSpeaking(false);
        setCurrentVideo(null);
    };

    return (
        <div className="flex flex-col h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 border-b border-gray-700/50">
                <button
                    onClick={() => router.push('/')}
                    className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back
                </button>
                <h1 className="text-xl font-semibold text-white flex items-center gap-2">
                    <span className="text-2xl">🎓</span>
                    AI Tutor
                    <span className="text-xs bg-gradient-to-r from-purple-500 to-pink-500 px-2 py-0.5 rounded-full">
                        Premium
                    </span>
                </h1>
                <button
                    onClick={() => setVoiceEnabled(!voiceEnabled)}
                    className={`p-2 rounded-lg transition-colors ${voiceEnabled ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'
                        }`}
                    title={voiceEnabled ? 'Voice enabled' : 'Voice disabled'}
                >
                    {voiceEnabled ? '🔊' : '🔇'}
                </button>
            </header>

            {/* Voice Notch */}
            <VoiceNotch
                isListening={isListening}
                isSpeaking={isSpeaking}
                onToggleListen={toggleListening}
            />

            {/* Main Content - Split View */}
            <main className="flex-1 flex overflow-hidden">
                {/* Left: Chat Panel */}
                <ChatPanel
                    messages={messages}
                    inputValue={inputValue}
                    isLoading={isLoading}
                    isListening={isListening}
                    onInputChange={setInputValue}
                    onSend={() => sendMessage(inputValue)}
                    onToggleListen={toggleListening}
                    onKeyDown={handleKeyDown}
                />

                {/* Right: Content Panel with sync playback */}
                <ContentPanel
                    video={currentVideo}
                    onGenerateNew={handleClearVideo}
                    isSpeaking={isSpeaking}
                />
            </main>
        </div>
    );
}
