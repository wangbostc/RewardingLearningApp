import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type { Lesson } from '@/lib/api-client';

export default function LessonsPage() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('userId')) {
      navigate('/login');
      return;
    }
    fetchLessons();
  }, [navigate]);

  const fetchLessons = async () => {
    try {
      const data = await apiClient.getLessons();
      setLessons(data.lessons || []);
    } catch (err) {
      console.error('Failed to load lessons:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = filter ? lessons.filter((l) => l.difficulty === filter) : lessons;

  const difficultyColor: Record<string, string> = {
    beginner: 'bg-green-100 text-green-700',
    elementary: 'bg-blue-100 text-blue-700',
    intermediate: 'bg-purple-100 text-purple-700',
    advanced: 'bg-red-100 text-red-700',
  };

  return (
    <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
      <Nav showBack />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">📚 Browse Lessons</h1>

        {/* Filter */}
        <div className="flex gap-2 mb-6 flex-wrap">
          <button
            onClick={() => setFilter('')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
              !filter ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            All
          </button>
          {['beginner', 'elementary', 'intermediate'].map((d) => (
            <button
              key={d}
              onClick={() => setFilter(d)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold capitalize transition ${
                filter === d ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {d}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading lessons...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {filtered.map((lesson) => (
              <div key={lesson.id} className="bg-white rounded-xl shadow-md p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-bold text-gray-900">{lesson.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${difficultyColor[lesson.difficulty] || 'bg-gray-100 text-gray-700'}`}>
                    {lesson.difficulty}
                  </span>
                </div>
                <p className="text-gray-500 text-sm mb-3">{lesson.description}</p>
                <div className="flex justify-between text-sm text-gray-400">
                  <span>⏱️ {lesson.estimated_duration} min</span>
                  <span>📝 {lesson.exercise_count} exercises</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
