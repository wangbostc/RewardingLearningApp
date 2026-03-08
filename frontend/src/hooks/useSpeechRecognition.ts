import { useState, useCallback, useRef } from 'react';

interface SpeechRecognitionHookResult {
  transcript: string;
  isListening: boolean;
  error: string | null;
  start: () => void;
  stop: () => void;
  reset: () => void;
  isSupported: boolean;
}

// Use `any` for the recognition instance to avoid Web Speech API type issues
// across different browsers and TypeScript configs
type SpeechRecognitionInstance = any;

function getSpeechRecognitionClass(): (new () => SpeechRecognitionInstance) | null {
  if (typeof window === 'undefined') return null;
  return (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition || null;
}

/**
 * Speech recognition hook.
 *
 * Uses Web Speech API (works on iPad Safari / Chrome with network).
 * The backend does the fuzzy matching via rapidfuzz, so even imperfect
 * transcripts get fair scoring.
 */
export function useSpeechRecognition(): SpeechRecognitionHookResult {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);

  const SpeechRecognitionClass = getSpeechRecognitionClass();
  const isSupported = !!SpeechRecognitionClass;

  const start = useCallback(() => {
    if (!SpeechRecognitionClass) {
      setError('Speech recognition is not supported in this browser.');
      return;
    }

    // Stop any existing recognition
    if (recognitionRef.current) {
      recognitionRef.current.abort();
    }

    const recognition = new SpeechRecognitionClass();
    recognition.lang = 'en-AU'; // Australian English
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      setTranscript('');
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      setTranscript(finalTranscript || interimTranscript);
    };

    recognition.onerror = (event: any) => {
      const errorCode = event.error;
      if (errorCode === 'no-speech') {
        setError("I didn't hear anything. Try again!");
      } else if (errorCode === 'audio-capture') {
        setError('No microphone found. Please check your device.');
      } else if (errorCode === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access.');
      } else {
        setError(`Oops! Something went wrong: ${errorCode}`);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch {
      setError('Failed to start speech recognition.');
      setIsListening(false);
    }
  }, [SpeechRecognitionClass]);

  const stop = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const reset = useCallback(() => {
    setTranscript('');
    setError(null);
    if (recognitionRef.current) {
      recognitionRef.current.abort();
    }
    setIsListening(false);
  }, []);

  return {
    transcript,
    isListening,
    error,
    start,
    stop,
    reset,
    isSupported,
  };
}
