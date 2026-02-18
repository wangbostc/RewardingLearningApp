'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api-client';

interface ProgressItem {
  lesson_id: number;
  lesson_title: string;
  status: string;
  progress_percentage: number;
  started_at: string;
  completed_at?: string;
}

interface Stats {
  total_points: number;
  level: number;
  streak_days: number;
  total_lessons_completed: number;
  current_difficulty: string;
  accuracy_rate: number;
}

export default function ProgressPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [progress, setProgress] = useState<ProgressItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    if (!storedUserId) {
      router.push('/auth/login');
      return;
    }

    setUserId(parseInt(storedUserId));
    fetchProgress(parseInt(storedUserId));
  }, [router]);

  const fetchProgress = async (id: number) => {
    try {
      const response = await apiClient.getUserProgress(id);
      setStats(response.stats);
      setProgress(response.progress || []);
    } catch (err) {
      console.error('Failed to load progress:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <Link href="/dashboard" className="text-2xl font-bold text-indigo-600">
              🎓 Learn English
            </Link>
          </div>
        </nav>
        <div className="flex items-center justify-center h-96">
          <div className="text-xl text-gray-600">Loading...</div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link href="/dashboard" className="text-2xl font-bold text-indigo-600">
              🎓 Learn English
            </Link>
            <Link href="/dashboard" className="text-indigo-600 hover:text-indigo-700">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-12">Your Learning Progress</h1>

        {/* Stats Summary */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Total Points</div>
              <div className="text-3xl font-bold text-indigo-600">{stats.total_points}</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Level</div>
              <div className="text-3xl font-bold text-yellow-500">{stats.level}</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Accuracy</div>
              <div className="text-3xl font-bold text-green-500">{stats.accuracy_rate.toFixed(1)}%</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Lessons Done</div>
              <div className="text-3xl font-bold text-purple-500">{stats.total_lessons_completed}</div>
            </div>
          </div>
        )}

        {/* Lessons Progress */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Lesson Progress</h2>

          {progress.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">No lessons started yet. Begin your learning journey!</p>
              <Link
                href="/lessons"
                className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700"
              >
                Browse Lessons
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {progress.map((item) => (
                <div key={item.lesson_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{item.lesson_title}</h3>
                      <p className="text-sm text-gray-600">
                        Started: {new Date(item.started_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(item.status)}`}>
                      {item.status === 'completed' ? '✓ Completed' : 'In Progress'}
                    </span>
                  </div>

                  <div className="mb-2">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{item.progress_percentage.toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${item.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {item.completed_at && (
                    <p className="text-sm text-green-600">
                      Completed: {new Date(item.completed_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Difficulty Info */}
        {stats && (
          <div className="mt-12 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Current Level</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <p className="text-gray-600 mb-2">Your current difficulty level:</p>
                <p className="text-3xl font-bold text-indigo-600 capitalize">{stats.current_difficulty}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-2">Lessons completed to advance:</p>
                <p className="text-lg text-gray-700">
                  {10 - (stats.total_lessons_completed % 10)} more lessons until next level
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

