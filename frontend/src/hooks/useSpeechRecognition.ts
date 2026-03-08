import { useState, useCallback, useMemo, useRef } from 'react';

type MicrophonePermissionState = 'unknown' | 'granted' | 'denied';

interface SpeechRecognitionHookResult {
  transcript: string;
  isListening: boolean;
  error: string | null;
  start: () => Promise<boolean>;
  stop: () => void;
  reset: () => void;
  isSupported: boolean;
  isSecureOrigin: boolean;
  permissionState: MicrophonePermissionState;
  helpText: string | null;
}

interface SpeechRecognitionAlternativeLike {
  transcript: string;
}

interface SpeechRecognitionResultLike {
  0: SpeechRecognitionAlternativeLike;
  isFinal: boolean;
}

interface SpeechRecognitionResultListLike {
  length: number;
  [index: number]: SpeechRecognitionResultLike;
}

interface SpeechRecognitionEventLike {
  resultIndex?: number;
  results: SpeechRecognitionResultListLike;
}

interface SpeechRecognitionErrorEventLike {
  error: string;
}

interface SpeechRecognitionInstance {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  onstart: (() => void) | null;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

declare global {
  interface Window {
    webkitSpeechRecognition?: new () => SpeechRecognitionInstance;
    SpeechRecognition?: new () => SpeechRecognitionInstance;
  }
}

function getSpeechRecognitionClass(): (new () => SpeechRecognitionInstance) | null {
  if (typeof window === 'undefined') return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function isSecureOrigin(): boolean {
  if (typeof window === 'undefined') return true;
  const localhostHosts = new Set(['localhost', '127.0.0.1']);
  return window.isSecureContext || localhostHosts.has(window.location.hostname);
}

function buildHelpText(isSupported: boolean, secureOrigin: boolean) {
  if (!isSupported) {
    return 'Use Safari on iPhone/iPad or Safari/Chrome on Mac for speech recognition.';
  }

  if (!secureOrigin) {
    return 'Microphone access on iPhone/iPad needs HTTPS (or localhost on the same device). Open the app on a secure URL.';
  }

  return 'Press and hold the microphone while reading, then release to stop. After that, you can play your recording and check the match.';
}

/**
 * Speech recognition hook.
 *
 * Uses Web Speech API plus a getUserMedia permission warm-up so it behaves
 * more reliably across macOS Safari/Chrome and iOS Safari.
 */
export function useSpeechRecognition(): SpeechRecognitionHookResult {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permissionState, setPermissionState] = useState<MicrophonePermissionState>('unknown');
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const transcriptRef = useRef('');
  const isStartingRef = useRef(false);
  const manualStopRef = useRef(false);

  const updateTranscript = useCallback((value: string) => {
    transcriptRef.current = value;
    setTranscript(value);
  }, []);

  const SpeechRecognitionClass = getSpeechRecognitionClass();
  const isSupported = !!SpeechRecognitionClass;
  const secureOrigin = isSecureOrigin();
  const helpText = useMemo(
    () => buildHelpText(isSupported, secureOrigin),
    [isSupported, secureOrigin]
  );

  const warmUpMicrophone = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      return true;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      stream.getTracks().forEach((track) => track.stop());
      setPermissionState('granted');
      return true;
    } catch (caughtError: unknown) {
      setPermissionState('denied');
      const micError = caughtError as { name?: string } | undefined;

      if (!secureOrigin) {
        setError(
          'Microphone access needs HTTPS on iPhone/iPad. Open the app from a secure address.'
        );
      } else if (micError?.name === 'NotAllowedError' || micError?.name === 'PermissionDeniedError') {
        setError('Microphone access denied. Please allow microphone access and try again.');
      } else {
        setError('Could not access the microphone. Please check microphone permissions.');
      }

      return false;
    }
  }, [secureOrigin]);

  const start = useCallback(async () => {
    if (!SpeechRecognitionClass) {
      setError('Speech recognition is not supported in this browser.');
      return false;
    }

    if (isStartingRef.current || isListening) {
      return false;
    }

    isStartingRef.current = true;
    manualStopRef.current = false;
    setError(null);
    updateTranscript('');

    const microphoneReady = await warmUpMicrophone();
    if (!microphoneReady) {
      isStartingRef.current = false;
      setIsListening(false);
      return false;
    }

    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }

    const recognition = new SpeechRecognitionClass();
    recognition.lang = 'en-AU';
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      isStartingRef.current = false;
    };

    recognition.onresult = (event: SpeechRecognitionEventLike) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex ?? 0; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += `${result[0].transcript} `;
        } else {
          interimTranscript += `${result[0].transcript} `;
        }
      }

      updateTranscript((finalTranscript || interimTranscript).trim());
    };

    recognition.onerror = (event: SpeechRecognitionErrorEventLike) => {
      const errorCode = event.error;
      if (errorCode === 'no-speech') {
        setError("I didn't hear anything. Hold the iPad/iPhone a bit closer and try again.");
      } else if (errorCode === 'audio-capture') {
        setError('No microphone was detected. Please check your device microphone.');
      } else if (errorCode === 'not-allowed') {
        setPermissionState('denied');
        setError('Microphone access denied. Please allow microphone access in browser settings.');
      } else if (errorCode === 'network') {
        setError('Speech recognition needs a browser-supported speech service. On iPhone/iPad, open the secure HTTPS address of this app.');
      } else {
        setError(`Speech recognition stopped: ${errorCode}`);
      }
      isStartingRef.current = false;
      setIsListening(false);
    };

    recognition.onend = () => {
      isStartingRef.current = false;
      setIsListening(false);
      if (!manualStopRef.current && !transcriptRef.current.trim()) {
        setError((currentError) => currentError ?? "I didn't catch any words. Try once more.");
      }
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
      return true;
    } catch {
      isStartingRef.current = false;
      setError('Failed to start speech recognition. Try tapping the microphone again.');
      setIsListening(false);
      recognitionRef.current = null;
      return false;
    }
  }, [SpeechRecognitionClass, isListening, updateTranscript, warmUpMicrophone]);

  const stop = useCallback(() => {
    manualStopRef.current = true;
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const reset = useCallback(() => {
    manualStopRef.current = true;
    updateTranscript('');
    setError(null);
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }
    isStartingRef.current = false;
    setIsListening(false);
  }, [updateTranscript]);

  return {
    transcript,
    isListening,
    error,
    start,
    stop,
    reset,
    isSupported,
    isSecureOrigin: secureOrigin,
    permissionState,
    helpText,
  };
}
