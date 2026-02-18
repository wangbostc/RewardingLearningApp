'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api-client';

interface Lesson {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  category: string;
  estimated_duration: number;
  exercise_count: number;
}

export default function LessonsPage() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [filteredLessons, setFilteredLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [difficulty, setDifficulty] = useState('');
  const [category, setCategory] = useState('');
  const router = useRouter();

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (!userId) {
      router.push('/auth/login');
      return;
    }
    fetchLessons();
  }, [router]);

  useEffect(() => {
    filterLessons();
  }, [lessons, difficulty, category]);

  const fetchLessons = async () => {
    try {
      const response = await apiClient.getLessons();
      setLessons(response.lessons || []);
    } catch (err) {
      console.error('Failed to load lessons:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterLessons = () => {
    let filtered = lessons;

    if (difficulty) {
      filtered = filtered.filter((l) => l.difficulty === difficulty);
    }

    if (category) {
      filtered = filtered.filter((l) => l.category === category);
    }

    setFilteredLessons(filtered);
  };

  const handleStartLesson = async (lessonId: number) => {
    const userId = localStorage.getItem('userId');
    if (!userId) return;

    try {
      await apiClient.startLesson(parseInt(userId), lessonId);
      router.push(`/lesson/${lessonId}`);
    } catch (err) {
      console.error('Failed to start lesson:', err);
    }
  };

  const difficultyLevels = ['beginner', 'elementary', 'intermediate', 'advanced'];
  const categories = ['vocab', 'grammar', 'conversation', 'listening'];

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-indigo-600">
              🎓 Learn English
            </Link>
            <Link href="/dashboard" className="text-indigo-600 hover:text-indigo-700">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-12">Browse Lessons</h1>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-12">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Lessons</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Levels</option>
                {difficultyLevels.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Lessons Grid */}
        {loading ? (
          <div className="text-center text-xl text-gray-600">Loading lessons...</div>
        ) : filteredLessons.length === 0 ? (
          <div className="text-center text-lg text-gray-600">No lessons found</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredLessons.map((lesson) => (
              <div key={lesson.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{lesson.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{lesson.description}</p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                      {lesson.difficulty}
                    </span>
                    <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                      {lesson.category}
                    </span>
                  </div>

                  <div className="text-sm text-gray-600 space-y-1">
                    <p>⏱️ {lesson.estimated_duration || '10'} minutes</p>
                    <p>📝 {lesson.exercise_count} exercises</p>
                  </div>
                </div>

                <button
                  onClick={() => handleStartLesson(lesson.id)}
                  className="w-full mt-4 py-2 px-4 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                >
                  Start Lesson
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

