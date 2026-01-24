'use client';

import React from 'react';

interface VoiceOrbProps {
    isListening: boolean;
    isSpeaking: boolean;
    onToggle: () => void;
}

export default function VoiceOrb({ isListening, isSpeaking, onToggle }: VoiceOrbProps) {
    const isActive = isListening || isSpeaking;

    if (!isActive) return null;

    return (
        <div className="flex justify-center py-3">
            <button
                onClick={onToggle}
                className={`
          relative flex items-center gap-3 px-5 py-2.5 rounded-full
          backdrop-blur-sm border transition-all
          ${isListening ? 'bg-blue-500/20 border-blue-500/50' : ''}
          ${isSpeaking ? 'bg-purple-500/20 border-purple-500/50' : ''}
        `}
            >
                {/* Animated Waves */}
                <div className="flex items-center gap-0.5 h-6">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <div
                            key={i}
                            className={`
                w-1 rounded-full transition-all
                ${isListening ? 'bg-blue-400' : 'bg-purple-400'}
              `}
                            style={{
                                height: `${Math.random() * 16 + 8}px`,
                                animation: isActive ? `wave 0.5s ease-in-out ${i * 0.1}s infinite alternate` : 'none'
                            }}
                        />
                    ))}
                </div>

                <span className={`text-sm font-medium ${isListening ? 'text-blue-400' : 'text-purple-400'}`}>
                    {isListening ? 'Listening...' : 'Speaking...'}
                </span>

                {isListening && (
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                )}
            </button>

            <style jsx>{`
        @keyframes wave {
          from { transform: scaleY(0.5); }
          to { transform: scaleY(1.5); }
        }
      `}</style>
        </div>
    );
}
