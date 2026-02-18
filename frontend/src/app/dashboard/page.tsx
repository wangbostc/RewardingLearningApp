'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api-client';

interface UserStats {
  total_points: number;
  level: number;
  streak_days: number;
  total_lessons_completed: number;
  current_difficulty: string;
  accuracy_rate: number;
  last_activity?: string;
}

export default function DashboardPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const [username, setUsername] = useState('');
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    const storedUsername = localStorage.getItem('username');

    if (!storedUserId) {
      router.push('/auth/login');
      return;
    }

    setUserId(parseInt(storedUserId));
    setUsername(storedUsername || '');
    fetchProgress(parseInt(storedUserId));
  }, [router]);

  const fetchProgress = async (id: number) => {
    try {
      const response = await apiClient.getUserProgress(id);
      setStats(response.stats);
    } catch (err: any) {
      setError('Failed to load progress');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    router.push('/');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="text-2xl font-bold text-indigo-600">🎓 Learn English</div>
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
            <Link href="/" className="text-2xl font-bold text-indigo-600">
              🎓 Learn English
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-gray-700">Welcome, {username}!</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            {/* Points Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Total Points</div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">{stats.total_points}</div>
              <div className="text-xs text-gray-500">Keep learning to earn more!</div>
            </div>

            {/* Level Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Current Level</div>
              <div className="text-4xl font-bold text-yellow-500 mb-2">{stats.level}</div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
                <div
                  className="bg-yellow-500 h-2 rounded-full"
                  style={{ width: `${(stats.level % 10) * 10}%` }}
                ></div>
              </div>
            </div>

            {/* Streak Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Current Streak</div>
              <div className="text-4xl font-bold text-red-500 mb-2">{stats.streak_days}</div>
              <div className="text-xs text-gray-500">days in a row</div>
            </div>

            {/* Accuracy Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">Accuracy Rate</div>
              <div className="text-4xl font-bold text-green-500 mb-2">{stats.accuracy_rate.toFixed(1)}%</div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${stats.accuracy_rate}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Link
            href="/lessons"
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition text-center"
          >
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Browse Lessons</h3>
            <p className="text-gray-600">Start or continue your lessons</p>
          </Link>

          <Link
            href="/progress"
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition text-center"
          >
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">View Progress</h3>
            <p className="text-gray-600">Track your learning journey</p>
          </Link>

          <Link
            href="/rewards"
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition text-center"
          >
            <div className="text-4xl mb-4">🏆</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Achievements</h3>
            <p className="text-gray-600">View your badges and rewards</p>
          </Link>
        </div>

        {/* Lessons Completed */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Progress</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold text-gray-900">Lessons Completed</h3>
                <p className="text-gray-600">{stats?.total_lessons_completed || 0} lessons</p>
              </div>
              <div className="text-3xl font-bold text-indigo-600">{stats?.total_lessons_completed || 0}</div>
            </div>

            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-semibold text-gray-900">Current Difficulty</h3>
                <p className="text-gray-600">{stats?.current_difficulty || 'beginner'}</p>
              </div>
              <div className="text-sm font-semibold text-indigo-600 uppercase">
                {stats?.current_difficulty || 'Beginner'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

