'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api-client';

interface Achievement {
  id: number;
  name: string;
  description: string;
  badge_icon: string;
  unlocked_at: string;
}

interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  points: number;
  level: number;
  accuracy_rate: number;
}

export default function RewardsPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'achievements' | 'leaderboard'>('achievements');
  const router = useRouter();

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    if (!storedUserId) {
      router.push('/auth/login');
      return;
    }

    setUserId(parseInt(storedUserId));
    fetchData(parseInt(storedUserId));
  }, [router]);

  const fetchData = async (id: number) => {
    try {
      const [achievementsRes, leaderboardRes] = await Promise.all([
        apiClient.getUserAchievements(id),
        apiClient.getLeaderboard(10),
      ]);

      setAchievements(achievementsRes.achievements || []);
      setLeaderboard(leaderboardRes.leaderboard || []);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
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
        <h1 className="text-4xl font-bold text-gray-900 mb-12">Achievements & Rewards</h1>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('achievements')}
            className={`px-6 py-4 font-semibold border-b-2 transition ${
              activeTab === 'achievements'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            🏆 Achievements ({achievements.length})
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`px-6 py-4 font-semibold border-b-2 transition ${
              activeTab === 'leaderboard'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            📊 Leaderboard ({leaderboard.length})
          </button>
        </div>

        {/* Achievements Tab */}
        {activeTab === 'achievements' && (
          <div>
            {achievements.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="text-6xl mb-4">🎯</div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">No Achievements Yet</h2>
                <p className="text-gray-600 mb-6">
                  Start learning and complete lessons to unlock achievements!
                </p>
                <Link
                  href="/lessons"
                  className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700"
                >
                  Start Learning
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className="bg-white rounded-lg shadow-md p-6 border-2 border-yellow-300 text-center hover:shadow-lg transition"
                  >
                    <div className="text-6xl mb-4">{achievement.badge_icon}</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{achievement.name}</h3>
                    <p className="text-gray-600 text-sm mb-4">{achievement.description}</p>
                    <p className="text-xs text-gray-500">
                      Unlocked: {new Date(achievement.unlocked_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Leaderboard Tab */}
        {activeTab === 'leaderboard' && (
          <div>
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Rank</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">User</th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Points</th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Level</th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Accuracy</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((entry, index) => (
                      <tr
                        key={entry.user_id}
                        className={`border-b border-gray-200 ${
                          entry.user_id === userId ? 'bg-indigo-50' : index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                        }`}
                      >
                        <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                          {entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : '#'}
                          {entry.rank}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                              {entry.username.charAt(0).toUpperCase()}
                            </div>
                            <span>{entry.username}</span>
                            {entry.user_id === userId && (
                              <span className="ml-2 px-2 py-1 bg-indigo-200 text-indigo-800 text-xs font-semibold rounded-full">
                                You
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right text-sm font-semibold text-indigo-600">
                          {entry.points}
                        </td>
                        <td className="px-6 py-4 text-right text-sm font-semibold text-yellow-600">
                          {entry.level}
                        </td>
                        <td className="px-6 py-4 text-right text-sm font-semibold text-green-600">
                          {entry.accuracy_rate.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

