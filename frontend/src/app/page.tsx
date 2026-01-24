'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import PromptInput from '../components/PromptInput';
import GenerateButton from '../components/GenerateButton';
import LoadingSpinner from '../components/LoadingSpinner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const EXAMPLE_PROMPTS = [
  "Explain gradient descent visually",
  "How does matrix multiplication work?",
  "Visualize the derivative of x squared",
  "Explain binary search algorithm",
  "Show how vectors are added",
];

// Video duration options
const DURATION_OPTIONS = [
  { value: 30, label: '30 seconds', description: 'Quick demo' },
  { value: 60, label: '1 minute', description: 'Brief explanation' },
  { value: 180, label: '3 minutes', description: 'Standard' },
  { value: 360, label: '6 minutes', description: 'Detailed' },
  { value: 600, label: '10 minutes', description: 'In-depth' },
];

export default function HomePage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [duration, setDuration] = useState(180); // Default 3 minutes

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    if (prompt.length > 300) {
      setError('Prompt must be 300 characters or less');
      return;
    }

    setLoading(true);
    setError('');
    setProgress(0);
    setStatus('Starting generation...');

    try {
      // Start generation
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: prompt.trim(),
          duration_seconds: duration,
          sample_mode: duration <= 60
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to start generation');
      }

      const { job_id } = await response.json();
      setStatus('Processing...');

      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_URL}/api/status/${job_id}`);
          const statusData = await statusRes.json();

          setProgress(statusData.progress || 0);
          setStatus(getStatusMessage(statusData.status, statusData.progress));

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            router.push(`/video/${job_id}`);
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setError(statusData.error_message || 'Generation failed');
            setLoading(false);
          }
        } catch (pollError) {
          console.error('Polling error:', pollError);
        }
      }, 2000);

      // Timeout after 45 minutes for 15+ minute videos
      setTimeout(() => {
        clearInterval(pollInterval);
        if (loading) {
          setError('Generation timed out. Please try again.');
          setLoading(false);
        }
      }, 2700000);  // 45 minutes

    } catch (err: any) {
      setError(err.message || 'An error occurred');
      setLoading(false);
    }
  };

  const getStatusMessage = (status: string, progress: number): string => {
    if (status === 'queued') return 'Queued for processing...';
    if (status === 'processing') {
      if (progress < 20) return 'Generating voiceovers...';
      if (progress < 80) return 'Rendering scenes...';
      if (progress < 95) return 'Assembling final video...';
      return 'Finishing up...';
    }
    return 'Processing...';
  };

  const handleExampleClick = (example: string) => {
    setPrompt(example);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="pt-8 pb-4 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
            Visual Explainer Generator
          </h1>
          <p className="text-gray-400 text-lg">
            Transform complex concepts into clear, animated explanations
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Prompt Section */}
        <div className="bg-gray-800 rounded-xl shadow-2xl p-6 mb-8">
          <label className="block text-gray-300 text-sm font-medium mb-2">
            What would you like to understand?
          </label>
          
          <PromptInput
            value={prompt}
            onChange={setPrompt}
            disabled={loading}
          />

          <div className="flex justify-between items-center mt-2 text-sm">
            <span className={`${prompt.length > 300 ? 'text-red-400' : 'text-gray-500'}`}>
              {prompt.length}/300 characters
            </span>
          </div>

          {/* Video Duration Selector */}
          <div className="mt-6">
            <label className="block text-gray-300 text-sm font-medium mb-3">
              Video Length
            </label>
            <div className="grid grid-cols-5 gap-2">
              {DURATION_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setDuration(option.value)}
                  disabled={loading}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    duration === option.value
                      ? 'border-blue-500 bg-blue-500/20 text-white'
                      : 'border-gray-600 bg-gray-700/50 text-gray-300 hover:border-gray-500'
                  } disabled:opacity-50`}
                >
                  <div className="text-sm font-medium">{option.label}</div>
                  <div className="text-xs text-gray-400">{option.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Example Prompts */}
          <div className="mt-4">
            <p className="text-gray-500 text-sm mb-2">Try an example:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  disabled={loading}
                  className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-full transition-colors disabled:opacity-50"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-900/50 border border-red-500 rounded-lg text-red-300 text-sm">
              {error}
            </div>
          )}

          {/* Generate Button */}
          <div className="mt-6">
            <GenerateButton
              onClick={handleGenerate}
              loading={loading}
              disabled={!prompt.trim() || prompt.length > 300}
            />
          </div>

          {/* Loading State */}
          {loading && (
            <div className="mt-6">
              <LoadingSpinner />
              <div className="text-center mt-4">
                <p className="text-gray-300">{status}</p>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-gray-500 text-sm mt-1">{progress}% complete</p>
              </div>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="text-2xl mb-2">🎯</div>
            <h3 className="text-white font-medium mb-1">Visual First</h3>
            <p className="text-gray-400 text-sm">
              Animated explanations that help you see and understand concepts
            </p>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="text-2xl mb-2">📐</div>
            <h3 className="text-white font-medium mb-1">Math & Tech Focus</h3>
            <p className="text-gray-400 text-sm">
              Specialized for mathematics, algorithms, ML, and physics
            </p>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="text-2xl mb-2">⚡</div>
            <h3 className="text-white font-medium mb-1">Quick & Free</h3>
            <p className="text-gray-400 text-sm">
              Generate videos in under 2 minutes, no account needed
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-500 text-sm">
        <p>Generate educational videos on any topic</p>
      </footer>
    </div>
  );
}