import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';

interface Achievement {
  id: number;
  name: string;
  description: string;
  badge_icon: string;
  unlocked_at: string;
}

export default function RewardsPage() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const userId = localStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [userId, navigate]);

  const fetchData = async () => {
    try {
      // Check for new achievements first
      await apiClient.checkAchievements(parseInt(userId!));
      const data = await apiClient.getUserAchievements(parseInt(userId!)) as any;
      setAchievements(data.achievements || []);
    } catch (err) {
      console.error('Failed to load achievements:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      <Nav showBack />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">🏆 My Achievements</h1>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : achievements.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🎯</div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">No achievements yet!</h2>
            <p className="text-gray-500">Keep reading to unlock badges and achievements.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((a) => (
              <div key={a.id} className="bg-white rounded-xl shadow-md p-6 text-center">
                <div className="text-5xl mb-3">{a.badge_icon}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-1">{a.name}</h3>
                <p className="text-sm text-gray-500 mb-2">{a.description}</p>
                <p className="text-xs text-gray-400">
                  Unlocked {new Date(a.unlocked_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

