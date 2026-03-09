import { useCallback, useEffect, useMemo, useState } from 'react';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type {
  ActivityAttemptRequest,
  ActivityAttemptResponse,
  EngineLessonCompleteResponse,
  EngineLessonDetail,
  EngineLessonSummary,
  LearningActivity,
  LearningPath,
  LearningUnit,
  ChildProfile,
} from '@/lib/api-client';

function parseUserId(): number | null {
  const raw = localStorage.getItem('userId');
  if (!raw) return null;
  const parsed = Number.parseInt(raw, 10);
  return Number.isNaN(parsed) ? null : parsed;
}

function getActivityData(activity: LearningActivity): Record<string, unknown> {
  if (!activity.activity_data || typeof activity.activity_data !== 'object' || Array.isArray(activity.activity_data)) {
    return {};
  }
  return activity.activity_data as Record<string, unknown>;
}

function parseCsvToList(input: string): string[] {
  return input
    .split(',')
    .map((token) => token.trim())
    .filter(Boolean);
}

export default function LessonEnginePage() {
  const userId = useMemo(() => parseUserId(), []);

  const [loading, setLoading] = useState(true);
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [units, setUnits] = useState<LearningUnit[]>([]);
  const [lessons, setLessons] = useState<EngineLessonSummary[]>([]);
  const [profiles, setProfiles] = useState<ChildProfile[]>([]);

  const [selectedPathId, setSelectedPathId] = useState<number | null>(null);
  const [selectedUnitId, setSelectedUnitId] = useState<number | null>(null);
  const [selectedLessonId, setSelectedLessonId] = useState<number | null>(null);
  const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null);

  const [lessonDetail, setLessonDetail] = useState<EngineLessonDetail | null>(null);
  const [activityIndex, setActivityIndex] = useState(0);
  const [answerInput, setAnswerInput] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [attemptResult, setAttemptResult] = useState<ActivityAttemptResponse | null>(null);
  const [completeResult, setCompleteResult] = useState<EngineLessonCompleteResponse | null>(null);
  const [activityStartMs, setActivityStartMs] = useState<number>(Date.now());
  const [error, setError] = useState<string | null>(null);

  const currentActivity = lessonDetail?.activities?.[activityIndex] ?? null;

  const resetActivityState = useCallback(() => {
    setAnswerInput('');
    setSubmitted(false);
    setAttemptResult(null);
    setError(null);
    setActivityStartMs(Date.now());
  }, []);

  useEffect(() => {
    const loadPathsAndProfiles = async () => {
      if (!userId) {
        setLoading(false);
        setError('Please log in first.');
        return;
      }

      try {
        const [pathResponse, profileResponse] = await Promise.all([
          apiClient.getLearningPaths(),
          apiClient.getProfiles(userId),
        ]);
        const availablePaths = pathResponse.paths ?? [];
        setPaths(availablePaths);
        setProfiles(profileResponse.profiles ?? []);
        if (availablePaths.length > 0) {
          setSelectedPathId(availablePaths[0].id);
        }
      } catch (caughtError) {
        setError('Failed to load lesson engine data.');
        console.error(caughtError);
      } finally {
        setLoading(false);
      }
    };

    void loadPathsAndProfiles();
  }, [userId]);

  useEffect(() => {
    const loadUnits = async () => {
      if (!selectedPathId) {
        setUnits([]);
        setSelectedUnitId(null);
        return;
      }

      try {
        const response = await apiClient.getPathUnits(selectedPathId);
        const pathUnits = response.units ?? [];
        setUnits(pathUnits);
        setSelectedUnitId(pathUnits.length > 0 ? pathUnits[0].id : null);
      } catch (caughtError) {
        setError('Failed to load units.');
        console.error(caughtError);
      }
    };

    void loadUnits();
  }, [selectedPathId]);

  useEffect(() => {
    const loadLessons = async () => {
      if (!selectedUnitId) {
        setLessons([]);
        setSelectedLessonId(null);
        return;
      }

      try {
        const response = await apiClient.getUnitLessons(selectedUnitId);
        const unitLessons = response.lessons ?? [];
        setLessons(unitLessons);
        setSelectedLessonId(unitLessons.length > 0 ? unitLessons[0].id : null);
      } catch (caughtError) {
        setError('Failed to load lessons.');
        console.error(caughtError);
      }
    };

    void loadLessons();
  }, [selectedUnitId]);

  useEffect(() => {
    const loadLessonDetail = async () => {
      if (!selectedLessonId) {
        setLessonDetail(null);
        return;
      }

      try {
        const response = await apiClient.getEngineLesson(selectedLessonId);
        setLessonDetail(response.lesson);
        setActivityIndex(0);
        setCompleteResult(null);
        resetActivityState();
      } catch (caughtError) {
        setError('Failed to load lesson details.');
        console.error(caughtError);
      }
    };

    void loadLessonDetail();
  }, [resetActivityState, selectedLessonId]);

  const buildAnswerPayload = useCallback((activity: LearningActivity, rawInput: string): ActivityAttemptRequest['answer'] | undefined => {
    const trimmed = rawInput.trim();
    if (!trimmed) return undefined;

    if (activity.type === 'sentence_order' || activity.type === 'sentence_builder') {
      return parseCsvToList(trimmed);
    }

    if (activity.type === 'memory_match') {
      return { matched_pairs: parseCsvToList(trimmed) };
    }

    if (activity.type === 'role_play') {
      return trimmed
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);
    }

    return trimmed;
  }, []);

  const submitCurrentActivity = useCallback(async () => {
    if (!currentActivity || !userId) return;

    const nextAnswer = buildAnswerPayload(currentActivity, answerInput);
    if (nextAnswer === undefined || nextAnswer === null) {
      setError('Please enter an answer first.');
      return;
    }
    const answer: Exclude<ActivityAttemptRequest['answer'], undefined | null> = nextAnswer;

    try {
      setError(null);
      const timeSpent = Math.max(1, Math.round((Date.now() - activityStartMs) / 1000));
      const payload = selectedProfileId
        ? { profile_id: selectedProfileId, answer, time_spent: timeSpent }
        : { user_id: userId, answer, time_spent: timeSpent };

      const result = await apiClient.submitActivityAttempt(currentActivity.id, payload as ActivityAttemptRequest);
      setAttemptResult(result);
      setSubmitted(true);
    } catch (caughtError) {
      setError('Failed to submit this activity. Please try again.');
      console.error(caughtError);
    }
  }, [activityStartMs, answerInput, buildAnswerPayload, currentActivity, selectedProfileId, userId]);

  const moveToNextActivity = useCallback(() => {
    if (!lessonDetail) return;
    const nextIndex = activityIndex + 1;
    if (nextIndex >= lessonDetail.activities.length) return;
    setActivityIndex(nextIndex);
    resetActivityState();
  }, [activityIndex, lessonDetail, resetActivityState]);

  const completeLesson = useCallback(async () => {
    if (!lessonDetail || !userId) return;

    try {
      const payload = selectedProfileId
        ? { profile_id: selectedProfileId }
        : { user_id: userId };
      const result = await apiClient.completeEngineLesson(lessonDetail.id, payload);
      setCompleteResult(result);
    } catch (caughtError) {
      setError('Failed to complete this lesson.');
      console.error(caughtError);
    }
  }, [lessonDetail, selectedProfileId, userId]);

  const renderActivityHelp = (activity: LearningActivity) => {
    const data = getActivityData(activity);

    if (activity.type === 'audio_to_picture' || activity.type === 'audio_to_action' || activity.type === 'word_to_picture') {
      const optionsValue = data.options ?? data.objects;
      const options = Array.isArray(optionsValue) ? optionsValue : [];
      return (
        <div className="space-y-3">
          {typeof data.audioUrl === 'string' && <audio controls src={data.audioUrl} className="w-full" />}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {options.map((option, index) => {
              const optionRecord = typeof option === 'object' && option !== null ? option as Record<string, unknown> : {};
              const optionId = String(optionRecord.id ?? index);
              const optionImage = typeof optionRecord.image === 'string' ? optionRecord.image : null;
              return (
                <button
                  key={optionId}
                  type="button"
                  onClick={() => setAnswerInput(optionId)}
                  className={`rounded-lg border p-3 text-left transition ${answerInput === optionId ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 bg-white'}`}
                >
                  <div className="font-semibold text-gray-800">{optionId}</div>
                  {optionImage && <div className="text-xs text-gray-500 mt-1">{optionImage}</div>}
                </button>
              );
            })}
          </div>
        </div>
      );
    }

    if (activity.type === 'story_question') {
      const options = Array.isArray(data.options) ? data.options : [];
      return (
        <div className="space-y-2">
          {options.map((option) => {
            const label = String(option);
            return (
              <button
                key={label}
                type="button"
                onClick={() => setAnswerInput(label)}
                className={`block w-full rounded-lg border px-3 py-2 text-left transition ${answerInput === label ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 bg-white'}`}
              >
                {label}
              </button>
            );
          })}
        </div>
      );
    }

    if (activity.type === 'role_play') {
      const dialogue = Array.isArray(data.dialogue) ? data.dialogue : [];
      return (
        <div className="space-y-3">
          <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-700">
            {dialogue.map((step, index) => {
              const line = typeof step === 'object' && step !== null ? step as Record<string, unknown> : {};
              const speaker = String(line.speaker ?? 'app');
              const text = String(line.text ?? line.expected ?? '');
              return <p key={`${speaker}-${index}`}>{speaker}: {text}</p>;
            })}
          </div>
          <textarea
            value={answerInput}
            onChange={(event) => setAnswerInput(event.target.value)}
            placeholder="Type each child reply on a new line"
            className="w-full min-h-24 rounded-lg border border-gray-300 p-3"
          />
        </div>
      );
    }

    const placeholder =
      activity.type === 'sentence_order' || activity.type === 'sentence_builder'
        ? 'Enter words in order separated by commas'
        : activity.type === 'memory_match'
          ? 'Enter matched IDs separated by commas'
          : 'Enter your answer';

    return (
      <textarea
        value={answerInput}
        onChange={(event) => setAnswerInput(event.target.value)}
        placeholder={placeholder}
        className="w-full min-h-24 rounded-lg border border-gray-300 p-3"
      />
    );
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
        <Nav showBack />
        <div className="mx-auto max-w-4xl p-8 text-center text-gray-600">Loading lesson engine...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
      <Nav showBack />
      <div className="mx-auto max-w-4xl p-4 sm:p-8 space-y-6">
        <div className="bg-white rounded-2xl shadow-md p-5">
          <h1 className="text-2xl font-bold text-gray-900">🧩 Lesson Engine Modules</h1>
          <p className="text-sm text-gray-600 mt-1">Try the new module types while keeping the existing reading flow unchanged.</p>
        </div>

        <div className="bg-white rounded-2xl shadow-md p-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <label className="text-sm font-medium text-gray-700">
            Path
            <select
              value={selectedPathId ?? ''}
              onChange={(event) => setSelectedPathId(Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-gray-300 p-2"
            >
              {paths.map((path) => (
                <option key={path.id} value={path.id}>{path.name}</option>
              ))}
            </select>
          </label>

          <label className="text-sm font-medium text-gray-700">
            Unit
            <select
              value={selectedUnitId ?? ''}
              onChange={(event) => setSelectedUnitId(Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-gray-300 p-2"
              disabled={units.length === 0}
            >
              {units.map((unit) => (
                <option key={unit.id} value={unit.id}>{unit.name}</option>
              ))}
            </select>
          </label>

          <label className="text-sm font-medium text-gray-700">
            Lesson
            <select
              value={selectedLessonId ?? ''}
              onChange={(event) => setSelectedLessonId(Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-gray-300 p-2"
              disabled={lessons.length === 0}
            >
              {lessons.map((lesson) => (
                <option key={lesson.id} value={lesson.id}>{lesson.title}</option>
              ))}
            </select>
          </label>

          <label className="text-sm font-medium text-gray-700">
            Profile (optional)
            <select
              value={selectedProfileId ?? ''}
              onChange={(event) => {
                const nextValue = event.target.value;
                setSelectedProfileId(nextValue ? Number(nextValue) : null);
              }}
              className="mt-1 w-full rounded-lg border border-gray-300 p-2"
            >
              <option value="">Use account user</option>
              {profiles.map((profile) => (
                <option key={profile.id} value={profile.id}>{profile.name}</option>
              ))}
            </select>
          </label>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 text-sm">{error}</div>
        )}

        {lessonDetail && currentActivity ? (
          <div className="bg-white rounded-2xl shadow-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">{lessonDetail.title}</h2>
              <span className="text-sm text-gray-500">Activity {activityIndex + 1} / {lessonDetail.activities.length}</span>
            </div>

            <div className="rounded-xl bg-indigo-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-indigo-600">{currentActivity.type}</p>
              <p className="text-lg font-semibold text-indigo-900 mt-1">{currentActivity.prompt}</p>
              {currentActivity.instructions && <p className="text-sm text-indigo-700 mt-1">{currentActivity.instructions}</p>}
            </div>

            {renderActivityHelp(currentActivity)}

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => void submitCurrentActivity()}
                disabled={submitted}
                className="rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white disabled:bg-indigo-300"
              >
                {submitted ? 'Submitted' : 'Submit Activity'}
              </button>

              {submitted && activityIndex + 1 < lessonDetail.activities.length && (
                <button
                  type="button"
                  onClick={moveToNextActivity}
                  className="rounded-lg bg-emerald-600 px-4 py-2 font-semibold text-white"
                >
                  Next Activity →
                </button>
              )}

              {submitted && activityIndex + 1 === lessonDetail.activities.length && (
                <button
                  type="button"
                  onClick={() => void completeLesson()}
                  className="rounded-lg bg-green-600 px-4 py-2 font-semibold text-white"
                >
                  Complete Lesson
                </button>
              )}
            </div>

            {attemptResult && (
              <div className={`rounded-lg p-3 text-sm font-semibold ${attemptResult.correct ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
                {attemptResult.correct ? 'Correct!' : 'Saved.'} +{attemptResult.score} points
              </div>
            )}

            {completeResult && (
              <div className={`rounded-lg p-3 text-sm font-semibold ${completeResult.completed ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
                Lesson score: {completeResult.score}% (unlock at {completeResult.unlock_threshold}%) · attempts tracked: {completeResult.attempts}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-md p-6 text-gray-600">No engine lesson is available for this selection yet.</div>
        )}
      </div>
    </main>
  );
}

