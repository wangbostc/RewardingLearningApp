import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type { ReadingSentence, SpeechCheckResult } from '@/lib/api-client';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';

type ReadState = 'loading' | 'ready' | 'listening' | 'checking' | 'correct' | 'tryAgain' | 'allDone';

export default function ReadPage() {
  const [sentence, setSentence] = useState<ReadingSentence | null>(null);
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [readState, setReadState] = useState<ReadState>('loading');
  const [result, setResult] = useState<SpeechCheckResult | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const navigate = useNavigate();

  const userId = localStorage.getItem('userId');
  const { transcript, isListening, error: speechError, start, stop, reset, isSupported } = useSpeechRecognition();

  const fetchNext = useCallback(async () => {
    if (!userId) return;
    setReadState('loading');
    try {
      const data = await apiClient.getNextSentence(parseInt(userId));
      if (data.sentence) {
        setSentence(data.sentence);
        setProgress(data.progress);
        setReadState('ready');
      } else {
        setProgress(data.progress);
        setReadState('allDone');
      }
    } catch (err) {
      console.error('Failed to load sentence:', err);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      navigate('/login');
      return;
    }
    fetchNext();
  }, [userId, navigate, fetchNext]);

  // When listening stops and we have a transcript, auto-check
  useEffect(() => {
    if (!isListening && transcript && readState === 'listening') {
      handleCheck(transcript);
    }
  }, [isListening, transcript]);

  const handleStartListening = () => {
    reset();
    setResult(null);
    setReadState('listening');
    start();
  };

  const handleStopListening = () => {
    stop();
  };

  const handleCheck = async (text: string) => {
    if (!userId || !sentence) return;
    setReadState('checking');

    try {
      const checkResult = await apiClient.checkSpeech(parseInt(userId), sentence.id, text);
      setResult(checkResult);

      if (checkResult.is_correct) {
        setReadState('correct');
        setShowConfetti(true);
        // Record the success
        await apiClient.recordReadingSuccess(parseInt(userId), sentence.id);
        setTimeout(() => setShowConfetti(false), 3000);
      } else {
        setReadState('tryAgain');
      }
    } catch (err) {
      console.error('Check failed:', err);
      setReadState('ready');
    }
  };

  const handleNext = () => {
    reset();
    setResult(null);
    fetchNext();
  };

  const handleRetry = () => {
    reset();
    setResult(null);
    setReadState('ready');
  };

  if (!userId) return null;

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100 relative overflow-hidden">
      <Nav showBack backTo="/dashboard" backLabel="Dashboard" />

      {/* Confetti */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center">
          <div className="text-8xl animate-bounce">🎉</div>
          <div className="absolute text-6xl animate-ping" style={{ top: '20%', left: '20%' }}>⭐</div>
          <div className="absolute text-6xl animate-ping" style={{ top: '15%', right: '25%' }}>🌟</div>
          <div className="absolute text-6xl animate-ping" style={{ bottom: '30%', left: '30%' }}>✨</div>
          <div className="absolute text-6xl animate-ping" style={{ bottom: '25%', right: '20%' }}>💫</div>
        </div>
      )}

      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{progress.completed} / {progress.total}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-indigo-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress.total > 0 ? (progress.completed / progress.total) * 100 : 0}%` }}
            />
          </div>
        </div>

        {/* All Done */}
        {readState === 'allDone' && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-8xl mb-6">🎊</div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Amazing!</h2>
            <p className="text-xl text-gray-600 mb-8">You've read all the sentences! Great job!</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-4 bg-indigo-600 text-white rounded-xl text-lg font-semibold hover:bg-indigo-700 transition"
            >
              Back to Dashboard
            </button>
          </div>
        )}

        {/* Loading */}
        {readState === 'loading' && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-6xl mb-4 animate-pulse">📖</div>
            <p className="text-xl text-gray-600">Loading next sentence...</p>
          </div>
        )}

        {/* Sentence Card */}
        {sentence && readState !== 'allDone' && readState !== 'loading' && (
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
            {/* Difficulty indicator */}
            <div className="flex justify-between items-center mb-4">
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`w-3 h-3 rounded-full ${
                      level <= sentence.difficulty_level ? 'bg-yellow-400' : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm text-gray-500">⭐ {sentence.points_value} points</span>
            </div>

            {/* The sentence to read */}
            <div className="text-center py-8">
              <p className="text-3xl md:text-4xl font-bold text-gray-900 leading-relaxed">
                {sentence.text}
              </p>
            </div>

            {/* Transcript display */}
            {(transcript || readState === 'listening') && (
              <div className="mt-4 p-4 bg-blue-50 rounded-xl">
                <p className="text-sm text-blue-600 font-medium mb-1">I heard:</p>
                <p className="text-lg text-blue-900">
                  {transcript || (
                    <span className="text-blue-400 animate-pulse">Listening...</span>
                  )}
                </p>
              </div>
            )}

            {/* Result feedback */}
            {result && readState === 'correct' && (
              <div className="mt-4 p-4 bg-green-50 rounded-xl text-center">
                <p className="text-2xl font-bold text-green-700 mb-1">{result.message}</p>
                <p className="text-lg text-green-600">+{result.points_earned} points!</p>
              </div>
            )}

            {result && readState === 'tryAgain' && (
              <div className="mt-4 p-4 bg-amber-50 rounded-xl text-center">
                <p className="text-xl font-bold text-amber-700 mb-1">{result.message}</p>
                <p className="text-sm text-amber-600">
                  Similarity: {result.similarity}% (need 75%)
                </p>
              </div>
            )}

            {/* Speech error */}
            {speechError && (
              <div className="mt-4 p-4 bg-red-50 rounded-xl text-center">
                <p className="text-red-700">{speechError}</p>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        {sentence && readState !== 'allDone' && readState !== 'loading' && (
          <div className="flex flex-col items-center gap-4">
            {readState === 'ready' && (
              <>
                {isSupported ? (
                  <button
                    onClick={handleStartListening}
                    className="w-32 h-32 rounded-full bg-red-500 hover:bg-red-600 text-white shadow-lg transition transform hover:scale-110 flex items-center justify-center"
                  >
                    <span className="text-5xl">🎤</span>
                  </button>
                ) : (
                  <p className="text-red-600 text-center">
                    Speech recognition is not supported on this device.
                    <br />Try using Safari or Chrome.
                  </p>
                )}
                <p className="text-gray-500">Tap the microphone and read the sentence</p>
              </>
            )}

            {readState === 'listening' && (
              <>
                <button
                  onClick={handleStopListening}
                  className="w-32 h-32 rounded-full bg-red-600 text-white shadow-lg animate-pulse flex items-center justify-center"
                >
                  <span className="text-5xl">⏹️</span>
                </button>
                <p className="text-red-600 font-semibold animate-pulse">
                  🔴 Listening... Read the sentence now!
                </p>
              </>
            )}

            {readState === 'checking' && (
              <div className="text-center">
                <div className="text-5xl animate-spin mb-4">⏳</div>
                <p className="text-gray-600">Checking your reading...</p>
              </div>
            )}

            {readState === 'correct' && (
              <button
                onClick={handleNext}
                className="px-10 py-4 bg-green-500 text-white rounded-xl text-xl font-bold hover:bg-green-600 transition shadow-lg"
              >
                Next Sentence →
              </button>
            )}

            {readState === 'tryAgain' && (
              <div className="flex gap-4">
                <button
                  onClick={handleRetry}
                  className="px-8 py-4 bg-amber-500 text-white rounded-xl text-lg font-bold hover:bg-amber-600 transition"
                >
                  🔄 Try Again
                </button>
                <button
                  onClick={handleNext}
                  className="px-8 py-4 bg-gray-400 text-white rounded-xl text-lg font-bold hover:bg-gray-500 transition"
                >
                  Skip →
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

