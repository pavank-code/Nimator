'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// User ID storage key
const USER_ID_KEY = 'nimator_user_id';

interface UserStats {
    total_videos: number;
    completed_videos: number;
    topics_studied: number;
    recent_activity_count: number;
}

interface ChatSession {
    session_id: string;
    title: string;
    topic: string | null;
    message_count: number;
    created_at: string;
    updated_at: string;
    job_id: string | null;
    video_url: string | null;
}

interface VideoRecord {
    video_id: string;
    job_id: string;
    prompt: string;
    topic: string;
    video_url: string | null;
    status: string;
    duration_seconds: number;
    scene_count: number;
    created_at: string;
    completed_at: string | null;
}

interface TopicStudy {
    topic_id: string;
    topic_name: string;
    category: string;
    video_count: number;
    prompts_count: number;
    last_studied: string;
    first_studied: string;
}

interface UserDashboard {
    user_id: string;
    stats: UserStats;
    recent_videos: VideoRecord[];
    topics: TopicStudy[];
    recent_activities: any[];
    recent_chats: ChatSession[];
}

interface UserContextType {
    userId: string | null;
    dashboard: UserDashboard | null;
    chatSessions: ChatSession[];
    videos: VideoRecord[];
    topics: TopicStudy[];
    loading: boolean;
    error: string | null;
    refreshDashboard: () => Promise<void>;
    createChatSession: (message: string, topic?: string) => Promise<ChatSession | null>;
    addMessageToSession: (sessionId: string, role: string, content: string) => Promise<void>;
    getChatSession: (sessionId: string) => Promise<any>;
    refreshVideos: () => Promise<void>;
    refreshTopics: () => Promise<void>;
    refreshChatSessions: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
    const [userId, setUserId] = useState<string | null>(null);
    const [dashboard, setDashboard] = useState<UserDashboard | null>(null);
    const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
    const [videos, setVideos] = useState<VideoRecord[]>([]);
    const [topics, setTopics] = useState<TopicStudy[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Initialize user ID on mount
    useEffect(() => {
        let storedUserId = localStorage.getItem(USER_ID_KEY);

        if (!storedUserId) {
            // Generate a new user ID
            storedUserId = crypto.randomUUID();
            localStorage.setItem(USER_ID_KEY, storedUserId);
        }

        setUserId(storedUserId);
    }, []);

    // Fetch dashboard data when user ID is available
    useEffect(() => {
        if (userId) {
            refreshDashboard();
        }
    }, [userId]);

    const getHeaders = () => ({
        'Content-Type': 'application/json',
        'X-User-Id': userId || '',
    });

    const refreshDashboard = async () => {
        if (!userId) return;

        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/user/dashboard`, {
                headers: getHeaders(),
            });

            if (response.ok) {
                const data = await response.json();
                setDashboard(data);
                setError(null);
            } else {
                console.error('Failed to fetch dashboard');
            }
        } catch (err) {
            console.error('Dashboard fetch error:', err);
            setError('Failed to load user data');
        } finally {
            setLoading(false);
        }
    };

    const refreshChatSessions = async () => {
        if (!userId) return;

        try {
            const response = await fetch(`${API_URL}/api/user/chat/history`, {
                headers: getHeaders(),
            });

            if (response.ok) {
                const data = await response.json();
                setChatSessions(data.sessions || []);
            }
        } catch (err) {
            console.error('Chat sessions fetch error:', err);
        }
    };

    const refreshVideos = async () => {
        if (!userId) return;

        try {
            const response = await fetch(`${API_URL}/api/user/videos`, {
                headers: getHeaders(),
            });

            if (response.ok) {
                const data = await response.json();
                setVideos(data.videos || []);
            }
        } catch (err) {
            console.error('Videos fetch error:', err);
        }
    };

    const refreshTopics = async () => {
        if (!userId) return;

        try {
            const response = await fetch(`${API_URL}/api/user/topics`, {
                headers: getHeaders(),
            });

            if (response.ok) {
                const data = await response.json();
                setTopics(data.topics || []);
            }
        } catch (err) {
            console.error('Topics fetch error:', err);
        }
    };

    const createChatSession = async (message: string, topic?: string): Promise<ChatSession | null> => {
        if (!userId) return null;

        try {
            const response = await fetch(`${API_URL}/api/user/chat`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ message, topic }),
            });

            if (response.ok) {
                const data = await response.json();
                await refreshChatSessions();
                return data;
            }
        } catch (err) {
            console.error('Create chat session error:', err);
        }
        return null;
    };

    const addMessageToSession = async (sessionId: string, role: string, content: string) => {
        if (!userId) return;

        try {
            await fetch(`${API_URL}/api/user/chat/${sessionId}/message`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ role, content }),
            });
        } catch (err) {
            console.error('Add message error:', err);
        }
    };

    const getChatSession = async (sessionId: string) => {
        if (!userId) return null;

        try {
            const response = await fetch(`${API_URL}/api/user/chat/${sessionId}`, {
                headers: getHeaders(),
            });

            if (response.ok) {
                return await response.json();
            }
        } catch (err) {
            console.error('Get chat session error:', err);
        }
        return null;
    };

    return (
        <UserContext.Provider
            value={{
                userId,
                dashboard,
                chatSessions,
                videos,
                topics,
                loading,
                error,
                refreshDashboard,
                createChatSession,
                addMessageToSession,
                getChatSession,
                refreshVideos,
                refreshTopics,
                refreshChatSessions,
            }}
        >
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}
