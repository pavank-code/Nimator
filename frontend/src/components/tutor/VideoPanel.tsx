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

export default function VideoPanel({ video, history = [], isSpeaking, onClose, onClear, onSelectVideo }: VideoPanelProps & { history?: VideoData[], onSelectVideo?: (video: VideoData) => void }) {
    const videoRef = useRef<HTMLVideoElement>(null);

    // Auto-play video when ready (muted)
    useEffect(() => {
        if (video?.status === 'completed' && video?.video_url && videoRef.current) {
            videoRef.current.muted = true;
            videoRef.current.play().catch(() => { });
        }
    }, [video?.status, video?.video_url]);

    const getStatusText = (v: VideoData) => {
        if (!v) return 'No video';
        switch (v.status) {
            case 'starting': return 'Initializing...';
            case 'queued': return 'Queued...';
            case 'processing':
                if (v.progress < 30) return 'Planning scenes...';
                if (v.progress < 70) return 'Rendering...';
                return 'Finalizing...';
            case 'completed': return 'Ready';
            case 'failed': return 'Failed';
            default: return 'Processing...';
        }
    };

    return (
        <div className="w-1/2 bg-[#171717] border-l border-white/10 flex flex-col transition-transform duration-300 ease-out animate-slide-in-right">
            {/* Header */}
            <div className="flex items-center justify-between h-14 px-4 border-b border-white/10 shrink-0">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🎬</span>
                    <span className="font-medium">Visual History</span>
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

            {/* Video Player Area */}
            <div className="p-4 shrink-0 border-b border-white/10 bg-[#121212]">
                {!video ? (
                    <div className="aspect-video rounded-xl bg-white/5 flex flex-col items-center justify-center text-center text-gray-500 border border-white/5">
                        <div className="w-12 h-12 mb-3 rounded-full bg-white/5 flex items-center justify-center">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <p className="text-sm">Select a video to play</p>
                    </div>
                ) : video.status === 'completed' && video.video_url ? (
                    <div>
                        <div className="rounded-xl overflow-hidden bg-black mb-3 shadow-lg border border-white/10">
                            <video
                                ref={videoRef}
                                src={`${API_URL}${video.video_url}`}
                                muted
                                controls
                                playsInline
                                className="w-full aspect-video"
                            />
                        </div>
                        <div className="flex items-start justify-between gap-4">
                            <div>
                                <h3 className="text-sm font-medium text-white mb-1 line-clamp-1">{video.prompt}</h3>
                                <p className="text-xs text-gray-400">{getStatusText(video)}</p>
                            </div>
                            <a
                                href={`${API_URL}${video.video_url}`}
                                download
                                className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition"
                                title="Download Video"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                            </a>
                        </div>
                    </div>
                ) : (
                    <div className="aspect-video rounded-xl bg-black/50 border border-white/10 flex flex-col items-center justify-center relative overflow-hidden">
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
                                    strokeDashoffset={`${2 * Math.PI * 44 * (1 - (video.progress || 0) / 100)}`}
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
                                <span className="text-xl font-bold">{video.progress || 0}%</span>
                            </div>
                        </div>
                        <p className="text-sm font-medium text-white/90">{getStatusText(video)}</p>
                        <p className="text-xs text-gray-500 mt-2 text-center px-4 line-clamp-1">{video.prompt}</p>
                    </div>
                )}
            </div>

            {/* History List */}
            <div className="flex-1 overflow-y-auto">
                <div className="p-4 space-y-3">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">My Visualizations</h3>
                    {history.length === 0 ? (
                        <p className="text-sm text-gray-600 text-center py-8">
                            No videos generated yet.<br />
                            Ask the tutor to "visualize" something!
                        </p>
                    ) : (
                        history.map((v) => (
                            <div
                                key={v.job_id}
                                onClick={() => onSelectVideo && onSelectVideo(v)}
                                className={`group p-3 rounded-xl border transition-all cursor-pointer ${video?.job_id === v.job_id
                                        ? 'bg-blue-600/10 border-blue-500/50'
                                        : 'bg-[#212121] border-white/5 hover:border-white/10 hover:bg-[#2a2a2a]'
                                    }`}
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div className="flex-1 min-w-0">
                                        <p className={`text-sm font-medium line-clamp-2 ${video?.job_id === v.job_id ? 'text-blue-400' : 'text-gray-200'
                                            }`}>
                                            {v.prompt || 'Untitled Visualization'}
                                        </p>
                                        <div className="flex items-center gap-2 mt-2">
                                            <span className={`w-2 h-2 rounded-full ${v.status === 'completed' ? 'bg-green-500' :
                                                    v.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
                                                }`} />
                                            <span className="text-xs text-gray-500">{getStatusText(v)}</span>
                                        </div>
                                    </div>
                                    {v.status === 'completed' && (
                                        <div className="w-16 h-10 bg-black/50 rounded flex items-center justify-center shrink-0">
                                            <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                                                <path d="M8 5v14l11-7z" />
                                            </svg>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
