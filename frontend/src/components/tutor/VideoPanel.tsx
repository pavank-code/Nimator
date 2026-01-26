'use client';

import React, { useRef, useEffect } from 'react';

interface VideoData {
    job_id: string;
    status: string;
    progress: number;
    video_url?: string;
    prompt?: string;
    voiceover_text?: string;
}

interface VideoPanelProps {
    video: VideoData | null;
    isSpeaking: boolean;
    onClose: () => void;
    onClear: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function VideoPanel({ video, isSpeaking, onClose, onClear }: VideoPanelProps) {
    const videoRef = useRef<HTMLVideoElement>(null);

    // Auto-play video when ready (muted)
    useEffect(() => {
        if (video?.status === 'completed' && video?.video_url && videoRef.current) {
            videoRef.current.muted = true;
            videoRef.current.play().catch(() => { });
        }
    }, [video?.status, video?.video_url]);

    const getStatusText = () => {
        if (!video) return 'No video';
        switch (video.status) {
            case 'starting': return 'Initializing...';
            case 'queued': return 'Queued...';
            case 'processing':
                if (video.progress < 30) return 'Planning scenes...';
                if (video.progress < 70) return 'Rendering...';
                return 'Finalizing...';
            case 'completed': return 'Ready';
            case 'failed': return 'Failed';
            default: return 'Processing...';
        }
    };

    return (
        <div className="w-96 bg-[#171717] border-l border-white/10 flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between h-14 px-4 border-b border-white/10">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🎬</span>
                    <span className="font-medium">Visual</span>
                    {isSpeaking && (
                        <span className="flex items-center gap-1 text-xs text-purple-400 bg-purple-500/20 px-2 py-0.5 rounded-full">
                            <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-pulse" />
                            Speaking
                        </span>
                    )}
                </div>
                <button onClick={onClose} className="p-1.5 hover:bg-white/10 rounded">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 p-4 overflow-y-auto">
                {!video ? (
                    <div className="h-full flex flex-col items-center justify-center text-center text-gray-500">
                        <div className="w-16 h-16 mb-4 rounded-full bg-white/5 flex items-center justify-center">
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <p className="text-sm mb-2">No video yet</p>
                        <p className="text-xs">Ask for a visual explanation</p>
                    </div>
                ) : video.status === 'completed' && video.video_url ? (
                    <div>
                        <div className="rounded-lg overflow-hidden bg-black mb-3">
                            <video
                                ref={videoRef}
                                src={`${API_URL}${video.video_url}`}
                                muted
                                controls
                                playsInline
                                className="w-full aspect-video"
                            />
                        </div>

                        <p className="text-sm text-gray-300 mb-3 line-clamp-2">{video.prompt}</p>

                        <div className="flex gap-2">
                            <a
                                href={`${API_URL}${video.video_url}`}
                                download
                                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Download
                            </a>
                            <button
                                onClick={onClear}
                                className="px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition"
                            >
                                Clear
                            </button>
                        </div>

                        <p className="text-xs text-gray-500 mt-3 text-center">
                            💡 Say &quot;make it slower&quot; to modify
                        </p>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center">
                        {/* Progress Ring */}
                        <div className="relative w-24 h-24 mb-4">
                            <svg className="w-full h-full -rotate-90">
                                <circle cx="48" cy="48" r="44" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="4" />
                                <circle
                                    cx="48" cy="48" r="44"
                                    fill="none"
                                    stroke="url(#progressGradient)"
                                    strokeWidth="4"
                                    strokeLinecap="round"
                                    strokeDasharray={`${2 * Math.PI * 44}`}
                                    strokeDashoffset={`${2 * Math.PI * 44 * (1 - (video?.progress || 0) / 100)}`}
                                    className="transition-all duration-300"
                                />
                                <defs>
                                    <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#3b82f6" />
                                        <stop offset="100%" stopColor="#8b5cf6" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-xl font-bold">{video?.progress || 0}%</span>
                            </div>
                        </div>

                        <p className="text-sm font-medium mb-1">{getStatusText()}</p>
                        <p className="text-xs text-gray-500 text-center max-w-[200px] line-clamp-2">
                            {video?.prompt}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
