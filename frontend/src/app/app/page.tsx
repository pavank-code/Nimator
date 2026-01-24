'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import VideoPlayerModal from '../../components/VideoPlayerModal';
import BlurText from '../../components/animations/BlurText';

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
  { value: 30, label: '30s', description: 'Quick demo' },
  { value: 60, label: '1 min', description: 'Brief' },
  { value: 180, label: '3 min', description: 'Standard' },
  { value: 360, label: '6 min', description: 'Detailed' },
  { value: 600, label: '10 min', description: 'In-depth' },
];

// Estimate generation time based on duration
const getEstimatedTime = (duration: number): string => {
  if (duration <= 60) return '~30 seconds';
  if (duration <= 180) return '~1-2 minutes';
  if (duration <= 360) return '~3-5 minutes';
  return '~5-10 minutes';
};

export default function HomePage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [duration, setDuration] = useState(180);
  const [showModal, setShowModal] = useState(false);

  // Handle Escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setShowModal(false);
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  const MAX_CHARS = 500;

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    if (prompt.length > MAX_CHARS) {
      setError(`Prompt must be ${MAX_CHARS} characters or less`);
      return;
    }

    setLoading(true);
    setShowModal(true);
    setError('');
    setProgress(0);
    setStatus('Starting generation...');

    try {
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

      setTimeout(() => {
        clearInterval(pollInterval);
        if (loading) {
          setError('Generation timed out. Please try again.');
          setLoading(false);
        }
      }, 2700000);

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

  const isGenerateEnabled = prompt.trim().length > 0 && prompt.length <= MAX_CHARS && !loading;

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Global Navigation Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-white/[0.08]">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo / Home Link */}
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 group"
          >
            <img
              src="/logo_128.png"
              alt="Nimator"
              className="h-8 w-8"
            />
            <span className="text-white font-semibold text-lg group-hover:text-red-400 transition-colors">
              Nimator
            </span>
          </button>

          {/* Right side nav */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/tutor')}
              className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-white border border-white/[0.1] hover:border-white/[0.2] rounded-lg transition-all text-sm font-medium"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              AI Tutor
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-28 pb-16 px-6">
        <div className="max-w-2xl mx-auto">
          {/* Hero Title with Animations */}
          <div className="text-center mb-12">
            {/* Animated Hero Text - All animations applied */}
            <h1 className="text-5xl md:text-7xl font-bold mb-4">
              <BlurText
                text="Hello, you!"
                animateBy="characters"
                delay={0}
                duration={0.6}
                direction="bottom"
                className="animate-gradient-text"
              />
            </h1>
            <p className="text-gray-400 text-lg">
              <BlurText
                text="Transform complex concepts into clear, animated explanations"
                animateBy="words"
                delay={0.4}
                duration={0.5}
                direction="bottom"
              />
            </p>
          </div>

          {/* Main Input Card */}
          <div className="bg-slate-900/50 border border-white/[0.08] rounded-2xl p-6 shadow-2xl">
            {/* Prompt Textarea with Inline Button */}
            <div className="relative">
              <label className="block text-gray-300 text-sm font-medium mb-3">
                What would you like to understand?
              </label>
              <div className="relative">
                <textarea
                  value={prompt}
                  onChange={(e) => {
                    setPrompt(e.target.value);
                    setError('');
                  }}
                  disabled={loading}
                  placeholder="e.g., Explain how neural networks learn through backpropagation..."
                  className="w-full h-32 px-4 py-3 bg-slate-900 border border-white/[0.1] rounded-xl text-white placeholder-gray-500 resize-none focus:outline-none focus:border-red-500/50 focus:ring-2 focus:ring-red-500/20 transition-all disabled:opacity-50"
                />
                {/* Character count */}
                <div className="absolute bottom-3 left-4">
                  <span className={`text-xs ${prompt.length > MAX_CHARS ? 'text-red-400' : 'text-gray-500'}`}>
                    {prompt.length}/{MAX_CHARS}
                  </span>
                </div>
              </div>
            </div>

            {/* Example Prompts */}
            <div className="mt-4">
              <p className="text-gray-500 text-xs mb-2 uppercase tracking-wider">Try an example</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_PROMPTS.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(example)}
                    disabled={loading}
                    className={`px-3 py-1.5 text-sm rounded-full transition-all disabled:opacity-50 ${prompt === example
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-white/[0.05] text-gray-400 hover:bg-white/[0.1] hover:text-white border border-transparent'
                      }`}
                  >
                    {example}
                  </button>
                ))}
              </div>
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
                    className={`p-3 rounded-xl border transition-all ${duration === option.value
                      ? 'border-red-500 bg-red-500/10 text-red-400'
                      : 'border-white/[0.08] bg-white/[0.02] text-gray-400 hover:border-white/[0.15] hover:text-white'
                      } disabled:opacity-50`}
                  >
                    <div className="text-sm font-semibold">{option.label}</div>
                    <div className="text-xs opacity-60 mt-0.5">{option.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center gap-2">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            {/* Generate Button with Time Estimate */}
            <div className="mt-6">
              <button
                onClick={handleGenerate}
                disabled={!isGenerateEnabled}
                className={`w-full py-4 px-6 rounded-xl font-semibold text-base transition-all flex items-center justify-center gap-3 ${isGenerateEnabled
                  ? 'bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-400 hover:to-pink-400 text-white shadow-lg shadow-red-500/25 hover:shadow-red-500/40 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-white/[0.05] text-gray-500 cursor-not-allowed'
                  }`}
              >
                {loading ? (
                  <>
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Generate Video
                  </>
                )}
              </button>

              {/* Time Estimate Micro-copy */}
              {!loading && (
                <p className="text-center text-gray-500 text-xs mt-3">
                  Estimated generation time: <span className="text-gray-400">{getEstimatedTime(duration)}</span>
                </p>
              )}

              {/* Loading indicator text (brief, since modal handles the main UI) */}
              {loading && (
                <p className="text-center text-red-400 text-sm mt-3 animate-pulse">
                  Generating your video...
                </p>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Video Player Modal */}
      <VideoPlayerModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        prompt={prompt}
        progress={progress}
        status={status}
      />
    </div>
  );
}