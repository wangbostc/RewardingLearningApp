import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type { UserProgressData } from '@/lib/api-client';

export default function DashboardPage() {
  const [stats, setStats] = useState<UserProgressData['stats'] | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const userId = localStorage.getItem('userId');
  const username = localStorage.getItem('username');
  const isAdmin = localStorage.getItem('isAdmin') === 'true';
  const parsedUserId = userId ? Number.parseInt(userId, 10) : Number.NaN;

  useEffect(() => {
    if (!userId || Number.isNaN(parsedUserId)) {
      navigate('/login');
      return;
    }

    const loadDashboard = async () => {
      try {
        const data = await apiClient.getUserProgress(parsedUserId);
        setStats(data.stats);
      } catch (err) {
        console.error('Failed to load progress:', err);
      } finally {
        setLoading(false);
      }
    };

    void loadDashboard();
  }, [navigate, parsedUserId, userId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
        <Nav />
        <div className="flex items-center justify-center h-96">
          <div className="text-xl text-gray-600">Loading...</div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
      <Nav />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            Hi {username}! 👋
          </h1>
          <p className="text-lg text-gray-600 mt-2">Ready to read today?</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-indigo-600">{stats.total_points}</div>
              <div className="text-sm text-gray-500 mt-1">⭐ Points</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-yellow-500">{stats.level}</div>
              <div className="text-sm text-gray-500 mt-1">📊 Level</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-green-500">{stats.streak_days}</div>
              <div className="text-sm text-gray-500 mt-1">🔥 Day Streak</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-purple-500">{stats.accuracy_rate.toFixed(0)}%</div>
              <div className="text-sm text-gray-500 mt-1">🎯 Accuracy</div>
            </div>
          </div>
        )}

        {/* Main Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link
            to="/read"
            className="bg-green-500 hover:bg-green-600 text-white rounded-2xl shadow-lg p-8 text-center transition transform hover:scale-105"
          >
            <div className="text-6xl mb-4">📖</div>
            <div className="text-2xl font-bold">Start Reading</div>
            <div className="text-green-100 mt-2">Read sentences and earn points!</div>
          </Link>

          <Link
            to="/lesson-engine"
            className="bg-indigo-500 hover:bg-indigo-600 text-white rounded-2xl shadow-lg p-8 text-center transition transform hover:scale-105"
          >
            <div className="text-6xl mb-4">🧩</div>
            <div className="text-2xl font-bold">Lesson Engine</div>
            <div className="text-indigo-100 mt-2">Try the new module activities.</div>
          </Link>

          <Link
            to="/shop"
            className="bg-purple-500 hover:bg-purple-600 text-white rounded-2xl shadow-lg p-8 text-center transition transform hover:scale-105"
          >
            <div className="text-6xl mb-4">🎁</div>
            <div className="text-2xl font-bold">Reward Shop</div>
            <div className="text-purple-100 mt-2">
              {stats ? `You have ${stats.total_points} points to spend!` : 'Trade points for rewards!'}
            </div>
          </Link>
        </div>

        {/* Secondary Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/lessons"
            className="bg-white hover:bg-gray-50 rounded-xl shadow-md p-6 text-center transition"
          >
            <div className="text-3xl mb-2">📚</div>
            <div className="font-semibold text-gray-900">Browse Lessons</div>
          </Link>

          <Link
            to="/progress"
            className="bg-white hover:bg-gray-50 rounded-xl shadow-md p-6 text-center transition"
          >
            <div className="text-3xl mb-2">📊</div>
            <div className="font-semibold text-gray-900">My Progress</div>
          </Link>

          <Link
            to="/rewards"
            className="bg-white hover:bg-gray-50 rounded-xl shadow-md p-6 text-center transition"
          >
            <div className="text-3xl mb-2">🏆</div>
            <div className="font-semibold text-gray-900">Achievements</div>
          </Link>
        </div>

        {/* Admin link */}
        {isAdmin && (
          <div className="mt-8 text-center">
            <Link
              to="/admin"
              className="inline-block px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition"
            >
              ⚙️ Admin Panel
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
