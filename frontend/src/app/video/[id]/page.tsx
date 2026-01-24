'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import VideoPlayer from '../../../components/VideoPlayer';
import DownloadButton from '../../../components/DownloadButton';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface VideoData {
    job_id: string;
    video_url: string;
    topic?: string;
    prompt?: string;
}

export default function VideoPage() {
    const params = useParams();
    const router = useRouter();
    const id = params?.id as string;
    
    const [videoData, setVideoData] = useState<VideoData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (id) {
            fetchVideo();
        }
    }, [id]);

    const fetchVideo = async () => {
        try {
            const response = await fetch(`${API_URL}/api/video/${id}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Video not found');
                }
                const data = await response.json();
                throw new Error(data.detail || 'Failed to fetch video');
            }
            
            const data = await response.json();
            setVideoData({
                ...data,
                video_url: `${API_URL}${data.video_url}`
            });
        } catch (err: any) {
            setError(err.message || 'Failed to load video');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-400">Loading video...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
                <div className="text-center max-w-md mx-auto px-4">
                    <div className="text-6xl mb-4">😕</div>
                    <h1 className="text-2xl font-bold text-white mb-2">Oops!</h1>
                    <p className="text-gray-400 mb-6">{error}</p>
                    <Link
                        href="/"
                        className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                        ← Back to Home
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
            {/* Header */}
            <header className="py-4 px-4 border-b border-gray-800">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <Link
                        href="/"
                        className="text-gray-400 hover:text-white transition-colors flex items-center gap-2"
                    >
                        ← Back
                    </Link>
                    <h1 className="text-white font-medium">Your Generated Video</h1>
                    <div className="w-16"></div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-5xl mx-auto px-4 py-8">
                {/* Video Player */}
                <div className="bg-gray-800 rounded-xl overflow-hidden shadow-2xl mb-6">
                    {videoData && <VideoPlayer videoUrl={videoData.video_url} />}
                </div>

                {/* Video Info & Actions */}
                <div className="bg-gray-800 rounded-xl p-6">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                            <h2 className="text-xl font-semibold text-white mb-1">
                                {videoData?.topic || 'Visual Explanation'}
                            </h2>
                            {videoData?.prompt && (
                                <p className="text-gray-400 text-sm">
                                    &quot;{videoData.prompt}&quot;
                                </p>
                            )}
                        </div>
                        <div className="flex gap-3">
                            {videoData && (
                                <DownloadButton videoUrl={videoData.video_url} />
                            )}
                            <Link
                                href="/"
                                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                            >
                                Create Another
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Share Section */}
                <div className="mt-6 text-center">
                    <p className="text-gray-500 text-sm">
                        Video ID: <code className="text-gray-400">{id}</code>
                    </p>
                    <p className="text-gray-600 text-xs mt-2">
                        Videos are automatically deleted after 1 hour
                    </p>
                </div>
            </main>
        </div>
    );
}