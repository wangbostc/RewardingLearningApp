import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type { UserProgressData } from '@/lib/api-client';

export default function ProgressPage() {
  const [data, setData] = useState<UserProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const userId = localStorage.getItem('userId');
  const parsedUserId = userId ? Number.parseInt(userId, 10) : Number.NaN;

  useEffect(() => {
    if (!userId || Number.isNaN(parsedUserId)) {
      navigate('/login');
      return;
    }

    const loadProgress = async () => {
      try {
        const result = await apiClient.getUserProgress(parsedUserId);
        setData(result);
      } catch (err) {
        console.error('Failed to load progress:', err);
      } finally {
        setLoading(false);
      }
    };

    void loadProgress();
  }, [navigate, parsedUserId, userId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
        <Nav showBack />
        <div className="flex items-center justify-center h-96 text-gray-600">Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
      <Nav showBack />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">📊 My Progress</h1>

        {data?.stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-indigo-600">{data.stats.total_points}</div>
              <div className="text-sm text-gray-500 mt-1">Total Points</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-yellow-500">{data.stats.level}</div>
              <div className="text-sm text-gray-500 mt-1">Level</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-green-500">{data.stats.accuracy_rate.toFixed(1)}%</div>
              <div className="text-sm text-gray-500 mt-1">Accuracy</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-5 text-center">
              <div className="text-3xl font-bold text-purple-500">{data.stats.total_lessons_completed}</div>
              <div className="text-sm text-gray-500 mt-1">Lessons Done</div>
            </div>
          </div>
        )}

        {data?.progress && data.progress.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Lesson History</h2>
            <div className="space-y-3">
              {data.progress.map((p, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-gray-900">{p.lesson_title}</p>
                    <p className="text-sm text-gray-500">{new Date(p.started_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-500 h-2 rounded-full"
                        style={{ width: `${p.progress_percentage}%` }}
                      />
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      p.status === 'completed' ? 'bg-green-100 text-green-700' :
                      p.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {p.status === 'completed' ? '✅' : p.status === 'in_progress' ? '📖' : '⏸️'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
