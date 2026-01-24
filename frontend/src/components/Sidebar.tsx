'use client';

import React from 'react';
import { useUser } from '../hooks/useUser';

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
    onSelectSession: (sessionId: string) => void;
    activeSessionId?: string | null;
}

export default function Sidebar({ isOpen, onClose, onSelectSession, activeSessionId }: SidebarProps) {
    const { dashboard, chatSessions, videos, topics, loading, refreshChatSessions } = useUser();

    React.useEffect(() => {
        if (isOpen) {
            refreshChatSessions();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 z-40 md:hidden"
                onClick={onClose}
            />

            {/* Sidebar */}
            <aside className={`
        fixed top-0 left-0 h-full w-80 bg-gray-900 border-r border-gray-700 z-50
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        flex flex-col
      `}>
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-700">
                    <h2 className="text-lg font-semibold text-white">History</h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-white transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Stats */}
                {dashboard && (
                    <div className="p-4 border-b border-gray-700">
                        <div className="grid grid-cols-2 gap-3">
                            <div className="bg-gray-800 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-blue-400">{dashboard.stats.total_videos}</div>
                                <div className="text-xs text-gray-400">Videos</div>
                            </div>
                            <div className="bg-gray-800 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-green-400">{dashboard.stats.topics_studied}</div>
                                <div className="text-xs text-gray-400">Topics</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* New Chat Button */}
                <div className="p-4">
                    <button
                        onClick={() => {
                            onSelectSession('new');
                            onClose();
                        }}
                        className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                     font-medium transition-colors flex items-center justify-center gap-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        New Explanation
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto">
                    {/* Recent Chats */}
                    <div className="p-4">
                        <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Prompts</h3>
                        {loading ? (
                            <div className="text-gray-500 text-sm">Loading...</div>
                        ) : chatSessions.length === 0 ? (
                            <div className="text-gray-500 text-sm">No history yet</div>
                        ) : (
                            <div className="space-y-2">
                                {chatSessions.map((session) => (
                                    <button
                                        key={session.session_id}
                                        onClick={() => {
                                            onSelectSession(session.session_id);
                                            onClose();
                                        }}
                                        className={`
                      w-full text-left p-3 rounded-lg transition-colors
                      ${activeSessionId === session.session_id
                                                ? 'bg-blue-600/20 border border-blue-500'
                                                : 'bg-gray-800 hover:bg-gray-700 border border-transparent'}
                    `}
                                    >
                                        <div className="text-sm text-white font-medium truncate">
                                            {session.title || 'Untitled'}
                                        </div>
                                        <div className="flex items-center gap-2 mt-1">
                                            {session.topic && (
                                                <span className="text-xs px-2 py-0.5 bg-gray-700 text-gray-300 rounded">
                                                    {session.topic}
                                                </span>
                                            )}
                                            {session.video_url && (
                                                <span className="text-xs text-green-400">🎬 Video</span>
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-500 mt-1">
                                            {new Date(session.updated_at).toLocaleDateString()}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Topics Studied */}
                    {dashboard && dashboard.topics.length > 0 && (
                        <div className="p-4 border-t border-gray-700">
                            <h3 className="text-sm font-medium text-gray-400 mb-3">Topics Studied</h3>
                            <div className="space-y-2">
                                {dashboard.topics.map((topic: any) => (
                                    <div
                                        key={topic.topic_id}
                                        className="bg-gray-800 rounded-lg p-3"
                                    >
                                        <div className="text-sm text-white font-medium">{topic.topic_name}</div>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="text-xs text-gray-400">{topic.video_count} videos</span>
                                            <span className="text-xs px-2 py-0.5 bg-gray-700 text-gray-300 rounded">
                                                {topic.category}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Recent Videos */}
                    {dashboard && dashboard.recent_videos.length > 0 && (
                        <div className="p-4 border-t border-gray-700">
                            <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Videos</h3>
                            <div className="space-y-2">
                                {dashboard.recent_videos.slice(0, 5).map((video: any) => (
                                    <div
                                        key={video.video_id}
                                        className="bg-gray-800 rounded-lg p-3"
                                    >
                                        <div className="text-sm text-white font-medium truncate">{video.prompt}</div>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className={`text-xs px-2 py-0.5 rounded ${video.status === 'completed'
                                                    ? 'bg-green-900 text-green-300'
                                                    : video.status === 'failed'
                                                        ? 'bg-red-900 text-red-300'
                                                        : 'bg-yellow-900 text-yellow-300'
                                                }`}>
                                                {video.status}
                                            </span>
                                            <span className="text-xs text-gray-400">{video.topic}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </aside>
        </>
    );
}
