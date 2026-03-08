import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

interface SpeakOptions {
  rate?: number;
}

interface SpeechSynthesisHookResult {
  isSupported: boolean;
  isSpeaking: boolean;
  error: string | null;
  speak: (text: string, options?: SpeakOptions) => boolean;
  stop: () => void;
}

function pickVoice(voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null {
  if (!voices.length) return null;

  return (
    voices.find((voice) => voice.lang.toLowerCase() === 'en-au') ||
    voices.find((voice) => voice.lang.toLowerCase().startsWith('en-au')) ||
    voices.find((voice) => voice.lang.toLowerCase().startsWith('en-')) ||
    voices[0] ||
    null
  );
}

function clampRate(rate: number | undefined): number {
  if (typeof rate !== 'number' || Number.isNaN(rate)) return 0.9;
  return Math.min(1.2, Math.max(0.5, rate));
}

export function useSpeechSynthesis(): SpeechSynthesisHookResult {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const isSupported = useMemo(
    () => typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window,
    []
  );

  useEffect(() => {
    if (!isSupported) return;

    const loadVoices = () => {
      setVoices(window.speechSynthesis.getVoices());
    };

    loadVoices();
    window.speechSynthesis.addEventListener('voiceschanged', loadVoices);

    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', loadVoices);
      window.speechSynthesis.cancel();
      utteranceRef.current = null;
      setIsSpeaking(false);
    };
  }, [isSupported]);

  const stop = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.cancel();
    utteranceRef.current = null;
    setIsSpeaking(false);
    setError(null);
  }, [isSupported]);

  const speak = useCallback(
    (text: string, options?: SpeakOptions) => {
      if (!isSupported) {
        setError('Read-aloud is not supported in this browser.');
        return false;
      }

      const trimmedText = text.trim();
      if (!trimmedText) {
        setError('There is no sentence to read aloud yet.');
        return false;
      }

      setError(null);
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(trimmedText);
      const selectedVoice = pickVoice(voices);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
        utterance.lang = selectedVoice.lang;
      } else {
        utterance.lang = 'en-AU';
      }

      utterance.rate = clampRate(options?.rate);
      utterance.pitch = 1;
      utterance.volume = 1;

      utterance.onstart = () => {
        setIsSpeaking(true);
        setError(null);
      };

      utterance.onend = () => {
        utteranceRef.current = null;
        setIsSpeaking(false);
      };

      utterance.onerror = () => {
        utteranceRef.current = null;
        setIsSpeaking(false);
        setError('Read-aloud could not start on this device. Please try again.');
      };

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
      return true;
    },
    [isSupported, voices]
  );

  return {
    isSupported,
    isSpeaking,
    error,
    speak,
    stop,
  };
}

