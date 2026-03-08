import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

interface AudioRecorderHookResult {
  isSupported: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  hasRecording: boolean;
  error: string | null;
  start: () => Promise<boolean>;
  stop: () => Promise<boolean>;
  play: () => Promise<boolean>;
  stopPlayback: () => void;
  reset: () => void;
}

function getPreferredMimeType(): string | undefined {
  if (typeof window === 'undefined' || typeof MediaRecorder === 'undefined') {
    return undefined;
  }

  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
  ];

  for (const mimeType of candidates) {
    if (typeof MediaRecorder.isTypeSupported === 'function' && MediaRecorder.isTypeSupported(mimeType)) {
      return mimeType;
    }
  }

  return undefined;
}

export function useAudioRecorder(): AudioRecorderHookResult {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasRecording, setHasRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioUrlRef = useRef<string | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const stopPromiseResolverRef = useRef<((hasAudio: boolean) => void) | null>(null);

  const isSupported = useMemo(
    () =>
      typeof window !== 'undefined' &&
      typeof navigator !== 'undefined' &&
      !!navigator.mediaDevices?.getUserMedia &&
      typeof MediaRecorder !== 'undefined',
    []
  );

  const stopPlayback = useCallback(() => {
    const audioElement = audioElementRef.current;
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
      audioElementRef.current = null;
    }
    setIsPlaying(false);
  }, []);

  const cleanupStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  const revokeRecordingUrl = useCallback(() => {
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    stopPlayback();
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;
    cleanupStream();
    revokeRecordingUrl();
    audioChunksRef.current = [];
    stopPromiseResolverRef.current?.(false);
    stopPromiseResolverRef.current = null;
    setIsRecording(false);
    setHasRecording(false);
    setError(null);
  }, [cleanupStream, revokeRecordingUrl, stopPlayback]);

  useEffect(() => reset, [reset]);

  const start = useCallback(async () => {
    if (!isSupported) {
      setError('Voice replay is not supported in this browser.');
      return false;
    }

    if (isRecording) {
      return false;
    }

    stopPlayback();
    revokeRecordingUrl();
    audioChunksRef.current = [];
    setHasRecording(false);
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      streamRef.current = stream;

      const mimeType = getPreferredMimeType();
      const mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        cleanupStream();
        mediaRecorderRef.current = null;
        setIsRecording(false);

        const hasAudioData = audioChunksRef.current.length > 0;
        if (hasAudioData) {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: mediaRecorder.mimeType || mimeType || 'audio/webm',
          });
          revokeRecordingUrl();
          audioUrlRef.current = URL.createObjectURL(audioBlob);
          setHasRecording(true);
        } else {
          setHasRecording(false);
        }

        audioChunksRef.current = [];
        stopPromiseResolverRef.current?.(hasAudioData);
        stopPromiseResolverRef.current = null;
      };

      mediaRecorder.onerror = () => {
        setError('Could not save your voice recording. Please try again.');
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      return true;
    } catch (caughtError: unknown) {
      cleanupStream();
      mediaRecorderRef.current = null;
      setIsRecording(false);
      setHasRecording(false);

      const recordingError = caughtError as { name?: string } | undefined;
      if (recordingError?.name === 'NotAllowedError' || recordingError?.name === 'PermissionDeniedError') {
        setError('Microphone access is needed to replay your own voice. Please allow microphone access.');
      } else {
        setError('Could not start recording your voice. Please try again.');
      }
      return false;
    }
  }, [cleanupStream, isRecording, isSupported, revokeRecordingUrl, stopPlayback]);

  const stop = useCallback(async () => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
      cleanupStream();
      setIsRecording(false);
      return false;
    }

    return await new Promise<boolean>((resolve) => {
      stopPromiseResolverRef.current = resolve;
      mediaRecorderRef.current?.stop();
    });
  }, [cleanupStream]);

  const play = useCallback(async () => {
    if (!audioUrlRef.current) {
      setError('There is no recorded reading to play yet.');
      return false;
    }

    stopPlayback();
    setError(null);

    const audioElement = new Audio(audioUrlRef.current);
    audioElementRef.current = audioElement;
    audioElement.onended = () => {
      audioElementRef.current = null;
      setIsPlaying(false);
    };
    audioElement.onerror = () => {
      audioElementRef.current = null;
      setIsPlaying(false);
      setError('Could not play your recorded reading. Please record it again.');
    };

    try {
      await audioElement.play();
      setIsPlaying(true);
      return true;
    } catch {
      audioElementRef.current = null;
      setIsPlaying(false);
      setError('Playback was blocked. Tap the button again to hear your reading.');
      return false;
    }
  }, [stopPlayback]);

  return {
    isSupported,
    isRecording,
    isPlaying,
    hasRecording,
    error,
    start,
    stop,
    play,
    stopPlayback,
    reset,
  };
}

