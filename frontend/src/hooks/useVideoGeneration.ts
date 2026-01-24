'use client';

import { useState, useCallback } from 'react';

interface JobStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  video_url?: string;
  error?: string;
}

interface UseVideoGenerationReturn {
  loading: boolean;
  jobId: string | null;
  status: JobStatus | null;
  error: string | null;
  generateVideo: (prompt: string) => Promise<string | null>;
  checkStatus: (jobId: string) => Promise<JobStatus | null>;
  reset: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useVideoGeneration(): UseVideoGenerationReturn {
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateVideo = useCallback(async (prompt: string): Promise<string | null> => {
    setLoading(true);
    setError(null);
    setStatus(null);
    
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start video generation');
      }

      const data = await response.json();
      setJobId(data.job_id);
      return data.job_id;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate video';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const checkStatus = useCallback(async (id: string): Promise<JobStatus | null> => {
    try {
      const response = await fetch(`${API_URL}/status/${id}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch status');
      }

      const data: JobStatus = await response.json();
      setStatus(data);
      
      if (data.status === 'failed') {
        setError(data.error || 'Video generation failed');
      }
      
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to check status';
      setError(message);
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setJobId(null);
    setStatus(null);
    setError(null);
  }, []);

  return {
    loading,
    jobId,
    status,
    error,
    generateVideo,
    checkStatus,
    reset,
  };
}

export default useVideoGeneration;