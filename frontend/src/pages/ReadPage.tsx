import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import TranscriptDiff from '@/components/TranscriptDiff';
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
  const [isPreparingMic, setIsPreparingMic] = useState(false);
  const [showDeviceHelp, setShowDeviceHelp] = useState(false);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const userId = localStorage.getItem('userId');
  const {
    transcript,
    isListening,
    error: speechError,
    start,
    stop,
    reset,
    isSupported,
    isSecureOrigin,
    permissionState,
    helpText,
  } = useSpeechRecognition();

  const currentOrigin = useMemo(
    () => (typeof window === 'undefined' ? '' : window.location.origin),
    []
  );
  const localhostUrl = useMemo(() => 'https://localhost:3000', []);
  const mobileNeedsHostSwap = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return ['localhost', '127.0.0.1'].includes(window.location.hostname);
  }, []);
  const suggestedMobileUrl = useMemo(() => {
    if (typeof window === 'undefined') return 'https://YOUR-MAC-IP:3000';
    if (mobileNeedsHostSwap) return 'https://YOUR-MAC-IP:3000';
    return window.location.origin;
  }, [mobileNeedsHostSwap]);

  const copyText = useCallback(async (value: string, label: string) => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        setCopyMessage(`${label} copied`);
      } else {
        setCopyMessage(`Copy this ${label}: ${value}`);
      }
    } catch {
      setCopyMessage(`Copy this ${label}: ${value}`);
    }
    window.setTimeout(() => setCopyMessage(null), 2500);
  }, []);

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
      setReadState('ready');
    }
  }, [userId]);

  const handleCheck = useCallback(async (text: string) => {
    if (!userId || !sentence) return;
    setReadState('checking');

    try {
      const checkResult = await apiClient.checkSpeech(parseInt(userId), sentence.id, text);
      setResult(checkResult);

      if (checkResult.is_correct) {
        setReadState('correct');
        setShowConfetti(true);
        await apiClient.recordReadingSuccess(parseInt(userId), sentence.id);
        setTimeout(() => setShowConfetti(false), 3000);
      } else {
        setReadState('tryAgain');
      }
    } catch (err) {
      console.error('Check failed:', err);
      setReadState('ready');
    }
  }, [sentence, userId]);

  useEffect(() => {
    if (!userId) {
      navigate('/login');
      return;
    }
    fetchNext();
  }, [userId, navigate, fetchNext]);

  useEffect(() => {
    if (!isListening && transcript && readState === 'listening') {
      handleCheck(transcript);
    }
  }, [handleCheck, isListening, readState, transcript]);

  const handleStartListening = useCallback(async () => {
    reset();
    setResult(null);
    setIsPreparingMic(true);

    const didStart = await start();
    setIsPreparingMic(false);
    setReadState(didStart ? 'listening' : 'ready');
  }, [reset, start]);

  const handleStopListening = () => {
    stop();
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

      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center">
          <div className="text-8xl animate-bounce">🎉</div>
          <div className="absolute text-6xl animate-ping" style={{ top: '20%', left: '20%' }}>⭐</div>
          <div className="absolute text-6xl animate-ping" style={{ top: '15%', right: '25%' }}>🌟</div>
          <div className="absolute text-6xl animate-ping" style={{ bottom: '30%', left: '30%' }}>✨</div>
          <div className="absolute text-6xl animate-ping" style={{ bottom: '25%', right: '20%' }}>💫</div>
        </div>
      )}

      <div className="max-w-3xl mx-auto px-4 py-8">
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

        <div className="mb-6 rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sky-950">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="font-semibold">Need help on MacBook, iPad, or iPhone?</p>
              <p className="mt-1 text-sm">
                The mic works best from the secure frontend URL. Tap below for quick setup steps.
              </p>
            </div>
            <button
              onClick={() => setShowDeviceHelp((value) => !value)}
              className="rounded-lg bg-white px-3 py-2 text-sm font-semibold text-sky-800 shadow-sm ring-1 ring-sky-200"
            >
              {showDeviceHelp ? 'Hide help' : 'Show help'}
            </button>
          </div>

          {copyMessage && (
            <div className="mt-3 rounded-lg bg-green-100 px-3 py-2 text-sm font-medium text-green-800">
              {copyMessage}
            </div>
          )}

          {showDeviceHelp && (
            <div className="mt-4 space-y-4 text-sm leading-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl bg-white p-4 ring-1 ring-sky-100">
                  <p className="font-semibold">Quick test on this laptop</p>
                  <p className="mt-2 text-sm text-sky-900">
                    Open the app on localhost and allow microphone access when the browser asks.
                  </p>
                  <div className="mt-3 rounded-lg bg-sky-50 px-3 py-2 font-mono text-xs text-sky-900 ring-1 ring-sky-100">
                    {localhostUrl}
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button
                      onClick={() => void copyText(localhostUrl, 'localhost URL')}
                      className="rounded-lg bg-sky-600 px-3 py-2 text-xs font-semibold text-white hover:bg-sky-700"
                    >
                      Copy localhost URL
                    </button>
                    <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
                      Works on MacBook localhost
                    </span>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 ring-1 ring-sky-100">
                  <p className="font-semibold">Current frontend URL</p>
                  <p className="mt-2 rounded-lg bg-sky-50 px-3 py-2 font-mono text-xs text-sky-900 ring-1 ring-sky-100">
                    {currentOrigin || localhostUrl}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button
                      onClick={() => void copyText(currentOrigin || localhostUrl, 'current URL')}
                      className="rounded-lg bg-white px-3 py-2 text-xs font-semibold text-sky-800 shadow-sm ring-1 ring-sky-200"
                    >
                      Copy current URL
                    </button>
                  </div>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-xl bg-white p-4 ring-1 ring-sky-100">
                  <p className="font-semibold">MacBook</p>
                  <ol className="mt-2 list-decimal pl-5">
                    <li>Open <span className="font-mono">https://localhost:3000</span>.</li>
                    <li>Allow microphone access in Safari or Chrome.</li>
                    <li>Tap the red microphone, then read aloud.</li>
                  </ol>
                </div>

                <div className="rounded-xl bg-white p-4 ring-1 ring-sky-100">
                  <p className="font-semibold">iPad / iPhone</p>
                  <ol className="mt-2 list-decimal pl-5">
                    <li>Use the same Wi‑Fi as your Mac.</li>
                    <li>Open the secure frontend URL from Safari.</li>
                    <li>Accept the local certificate warning once if Safari asks.</li>
                    <li>Allow microphone access.</li>
                  </ol>
                </div>

                <div className="rounded-xl bg-white p-4 ring-1 ring-sky-100">
                  <p className="font-semibold">If the mic still fails</p>
                  <ul className="mt-2 list-disc pl-5">
                    <li>Use Safari on iPhone/iPad.</li>
                    <li>Reload the page after granting permission.</li>
                    <li>Hold the device a little closer when reading.</li>
                  </ul>
                </div>
              </div>

              {mobileNeedsHostSwap && (
                <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
                  <p className="font-semibold">Mobile URL to use from iPad/iPhone</p>
                  <p className="mt-2 text-sm">
                    On iPad/iPhone, <span className="font-semibold">localhost</span> points to the phone itself.
                    Use your Mac's local network address instead.
                  </p>
                  <span className="mt-2 block rounded-lg bg-white px-3 py-2 font-mono text-xs ring-1 ring-amber-100">
                    {suggestedMobileUrl}
                  </span>
                  <button
                    onClick={() => void copyText(suggestedMobileUrl, 'mobile URL')}
                    className="mt-3 rounded-lg bg-amber-600 px-3 py-2 text-xs font-semibold text-white hover:bg-amber-700"
                  >
                    Copy mobile URL template
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {!isSecureOrigin && (
          <div className="mb-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
            <p className="font-semibold">Microphone tip for iPad and iPhone</p>
            <p className="mt-1 text-sm">
              Open this app on an HTTPS address from your Mac so Safari will allow microphone access.
            </p>
          </div>
        )}

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

        {readState === 'loading' && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-6xl mb-4 animate-pulse">📖</div>
            <p className="text-xl text-gray-600">Loading next sentence...</p>
          </div>
        )}

        {sentence && readState !== 'allDone' && readState !== 'loading' && (
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
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

            <div className="text-center py-8">
              <p className="text-3xl md:text-4xl font-bold text-gray-900 leading-relaxed">
                {sentence.text}
              </p>
            </div>

            <div className="mt-4 rounded-xl bg-blue-50 p-4">
              <p className="text-sm font-medium text-blue-700 mb-1">Microphone status</p>
              <p className="text-sm text-blue-900">{helpText}</p>
              <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold">
                <span className={`rounded-full px-3 py-1 ${isSupported ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {isSupported ? 'Speech supported' : 'Speech unsupported'}
                </span>
                <span className={`rounded-full px-3 py-1 ${permissionState === 'granted' ? 'bg-green-100 text-green-700' : permissionState === 'denied' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}`}>
                  Mic permission: {permissionState}
                </span>
                <span className={`rounded-full px-3 py-1 ${isSecureOrigin ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-800'}`}>
                  {isSecureOrigin ? 'Secure origin' : 'Needs HTTPS for mobile mic'}
                </span>
              </div>
            </div>

            {(transcript || readState === 'listening' || result) && (
              <div className="mt-4 space-y-4">
                {result && !result.is_correct ? (
                  <>
                    <TranscriptDiff
                      title="Read this sentence"
                      tokens={result.expected_tokens}
                      counterpartTokens={result.heard_tokens}
                      emptyText={sentence.text}
                    />
                    <TranscriptDiff
                      title="What the device heard"
                      tokens={result.heard_tokens}
                      counterpartTokens={result.expected_tokens}
                      emptyText={transcript || 'No transcript captured.'}
                    />
                    <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                      <span className="rounded-full bg-red-100 px-3 py-1 text-red-700">Wrong word / letters</span>
                      <span className="rounded-full bg-amber-100 px-3 py-1 text-amber-800">Missing word</span>
                      <span className="rounded-full bg-purple-100 px-3 py-1 text-purple-800">Extra word</span>
                    </div>
                  </>
                ) : (
                  <div className="rounded-xl bg-blue-50 p-4">
                    <p className="text-sm font-medium text-blue-600 mb-1">I heard:</p>
                    <p className="text-lg text-blue-900">
                      {transcript || <span className="text-blue-400 animate-pulse">Listening...</span>}
                    </p>
                  </div>
                )}
              </div>
            )}

            {result && readState === 'correct' && (
              <div className="mt-4 p-4 bg-green-50 rounded-xl text-center">
                <p className="text-2xl font-bold text-green-700 mb-1">{result.message}</p>
                <p className="text-lg text-green-600">
                  {result.points_earned > 0 ? `+${result.points_earned} points!` : 'No extra points this time, but great reading!'}
                </p>
              </div>
            )}

            {result && readState === 'tryAgain' && (
              <div className="mt-4 p-4 bg-amber-50 rounded-xl text-center">
                <p className="text-xl font-bold text-amber-700 mb-1">{result.message}</p>
                <p className="text-sm text-amber-700">
                  Similarity: {result.similarity}% (need 75%)
                </p>
              </div>
            )}

            {speechError && (
              <div className="mt-4 p-4 bg-red-50 rounded-xl text-center">
                <p className="text-red-700">{speechError}</p>
              </div>
            )}
          </div>
        )}

        {sentence && readState !== 'allDone' && readState !== 'loading' && (
          <div className="flex flex-col items-center gap-4">
            {readState === 'ready' && (
              <>
                {isSupported ? (
                  <button
                    onClick={() => { void handleStartListening(); }}
                    disabled={isPreparingMic}
                    className="w-32 h-32 rounded-full bg-red-500 hover:bg-red-600 disabled:bg-red-300 text-white shadow-lg transition transform hover:scale-110 flex items-center justify-center"
                  >
                    <span className="text-5xl">🎤</span>
                  </button>
                ) : (
                  <p className="text-red-600 text-center">
                    Speech recognition is not supported on this device.
                    <br />Try Safari on iPhone/iPad or Safari/Chrome on Mac.
                  </p>
                )}
                <p className="text-gray-500 text-center">
                  {isPreparingMic ? 'Getting the microphone ready...' : 'Tap the microphone and read the sentence'}
                </p>
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
                <p className="text-red-600 font-semibold animate-pulse text-center">
                  🔴 Listening... Read the sentence now, then tap stop.
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
              <div className="flex flex-wrap justify-center gap-4">
                <button
                  onClick={handleRetry}
                  className="px-8 py-4 bg-amber-500 text-white rounded-xl text-lg font-bold hover:bg-amber-600 transition"
                >
                  🔄 Try Again
                </button>
                {transcript && (
                  <button
                    onClick={() => void handleCheck(transcript)}
                    className="px-8 py-4 bg-indigo-500 text-white rounded-xl text-lg font-bold hover:bg-indigo-600 transition"
                  >
                    Check Again
                  </button>
                )}
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

