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

interface ContentPanelProps {
    video: VideoData | null;
    onGenerateNew: () => void;
    isSpeaking?: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ContentPanel({ video, onGenerateNew, isSpeaking = false }: ContentPanelProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const wasCompletedRef = useRef(false);

    // Auto-play video when it becomes ready (muted - voice comes separately)
    useEffect(() => {
        if (video?.status === 'completed' && video?.video_url && !wasCompletedRef.current) {
            wasCompletedRef.current = true;
            // Small delay to ensure video element is mounted
            setTimeout(() => {
                if (videoRef.current) {
                    videoRef.current.muted = true; // Video plays WITHOUT audio
                    videoRef.current.play().catch(console.error);
                }
            }, 100);
        }

        // Reset when video changes
        if (!video || video.status !== 'completed') {
            wasCompletedRef.current = false;
        }
    }, [video?.status, video?.video_url]);

    const getStatusMessage = () => {
        if (!video) return '';
        switch (video.status) {
            case 'starting': return 'Initializing generation...';
            case 'queued': return 'Queued for processing...';
            case 'processing':
                if (video.progress < 20) return 'Planning scenes...';
                if (video.progress < 50) return 'Rendering animations...';
                if (video.progress < 80) return 'Assembling video...';
                return 'Finalizing...';
            case 'completed': return 'Video ready!';
            case 'failed': return 'Generation failed';
            default: return 'Processing...';
        }
    };

    return (
        <div className="w-1/2 flex flex-col bg-gray-850 p-6">
            {/* Panel Header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <span>🎬</span>
                    Visual Content
                    {isSpeaking && (
                        <span className="text-xs bg-purple-600 px-2 py-0.5 rounded-full animate-pulse">
                            🔊 Speaking
                        </span>
                    )}
                </h2>
                {video && video.status === 'completed' && (
                    <button
                        onClick={onGenerateNew}
                        className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                    >
                        Clear
                    </button>
                )}
            </div>

            {/* Content Area */}
            <div className="flex-1 flex items-center justify-center">
                {!video ? (
                    // Empty State
                    <div className="text-center max-w-md">
                        <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gray-700/50 flex items-center justify-center">
                            <svg className="w-12 h-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-medium text-white mb-2">No Video Yet</h3>
                        <p className="text-gray-400 mb-4">
                            Ask the AI tutor a question that would benefit from visual explanation,
                            and a video will be generated here.
                        </p>
                        <div className="text-sm text-gray-500">
                            Try asking:
                            <ul className="mt-2 space-y-1">
                                <li className="text-gray-400">&quot;Show me gradient descent visually&quot;</li>
                                <li className="text-gray-400">&quot;Visualize how sorting algorithms work&quot;</li>
                                <li className="text-gray-400">&quot;Explain the Pythagorean theorem with animation&quot;</li>
                            </ul>
                        </div>
                    </div>
                ) : video.status === 'completed' && video.video_url ? (
                    // Video Player - MUTED (voice comes from TTS separately)
                    <div className="w-full">
                        <div className="relative rounded-xl overflow-hidden bg-black shadow-2xl">
                            {/* Sync indicator */}
                            {isSpeaking && (
                                <div className="absolute top-3 right-3 z-10 flex items-center gap-2 bg-purple-600/80 backdrop-blur-sm px-3 py-1.5 rounded-full">
                                    <div className="flex gap-1">
                                        {[0, 1, 2].map(i => (
                                            <div
                                                key={i}
                                                className="w-1 h-3 bg-white rounded-full animate-bounce"
                                                style={{ animationDelay: `${i * 100}ms` }}
                                            />
                                        ))}
                                    </div>
                                    <span className="text-xs text-white font-medium">Speaking</span>
                                </div>
                            )}

                            <video
                                ref={videoRef}
                                src={`${API_URL}${video.video_url}`}
                                muted // Video is always muted - voice assistant speaks
                                loop={false}
                                playsInline
                                controls
                                className="w-full aspect-video"
                            >
                                Your browser does not support video playback.
                            </video>
                        </div>

                        {/* Video Info */}
                        <div className="mt-4 bg-gray-800/50 rounded-lg p-4">
                            <p className="text-white font-medium mb-2">{video.prompt || 'Generated Video'}</p>
                            <div className="flex gap-3">
                                <a
                                    href={`${API_URL}${video.video_url}`}
                                    download
                                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors text-sm"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                    Download MP4
                                </a>
                                <button
                                    onClick={onGenerateNew}
                                    className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    Request Changes
                                </button>
                            </div>
                            <p className="text-xs text-gray-500 mt-3">
                                💡 The AI tutor narrates the video. Ask for changes like &quot;make it slower&quot; or &quot;add more detail&quot;
                            </p>
                        </div>
                    </div>
                ) : (
                    // Loading State
                    <div className="text-center">
                        {/* Animated Loading */}
                        <div className="w-32 h-32 mx-auto mb-6 relative">
                            {/* Outer ring */}
                            <div className="absolute inset-0 rounded-full border-4 border-gray-700" />
                            {/* Progress ring */}
                            <svg className="absolute inset-0 w-full h-full -rotate-90">
                                <circle
                                    cx="64"
                                    cy="64"
                                    r="60"
                                    fill="none"
                                    stroke="url(#gradient)"
                                    strokeWidth="4"
                                    strokeLinecap="round"
                                    strokeDasharray={`${2 * Math.PI * 60}`}
                                    strokeDashoffset={`${2 * Math.PI * 60 * (1 - (video?.progress || 0) / 100)}`}
                                    className="transition-all duration-500"
                                />
                                <defs>
                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#3b82f6" />
                                        <stop offset="100%" stopColor="#8b5cf6" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            {/* Center content */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-2xl font-bold text-white">{video?.progress || 0}%</span>
                            </div>
                        </div>

                        <h3 className="text-xl font-medium text-white mb-2">Generating Video</h3>
                        <p className="text-gray-400 mb-2">{getStatusMessage()}</p>
                        <p className="text-xs text-gray-500 mb-4">
                            Video renders silently • Voice narration plays when ready
                        </p>

                        {video?.prompt && (
                            <p className="text-sm text-gray-500 max-w-xs mx-auto">
                                &quot;{video.prompt}&quot;
                            </p>
                        )}

                        {/* Animated dots */}
                        <div className="flex justify-center gap-1 mt-4">
                            {[0, 1, 2].map(i => (
                                <div
                                    key={i}
                                    className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                                    style={{ animationDelay: `${i * 150}ms` }}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
