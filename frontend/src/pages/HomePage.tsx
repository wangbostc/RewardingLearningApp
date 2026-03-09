import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function HomePage() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => Boolean(localStorage.getItem('userId')));
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    navigate('/');
  };

  return (
    <main className="min-h-screen bg-linear-to-b from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="text-2xl font-bold text-indigo-600">🎓 Learn English</div>
            <div className="flex gap-4">
              {isLoggedIn ? (
                <>
                  <button onClick={() => navigate('/dashboard')} className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
                    Dashboard
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-700"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-700">Login</Link>
                  <Link to="/register" className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">Sign Up</Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Read Aloud, Earn Rewards! 🎉
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Read English sentences out loud, and earn points for every sentence you get right.
            Trade your points for awesome rewards!
          </p>

          {!isLoggedIn ? (
            <div className="flex gap-4 justify-center">
              <Link to="/register" className="px-8 py-4 rounded-lg bg-indigo-600 text-white text-lg font-semibold hover:bg-indigo-700 transition">
                Get Started
              </Link>
              <Link to="/login" className="px-8 py-4 rounded-lg border-2 border-indigo-600 text-indigo-600 text-lg font-semibold hover:bg-indigo-50 transition">
                Login
              </Link>
            </div>
          ) : (
            <Link to="/read" className="inline-block px-10 py-5 rounded-xl bg-green-500 text-white text-2xl font-bold hover:bg-green-600 transition shadow-lg">
              📖 Start Reading!
            </Link>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-5xl mb-4">🎤</div>
            <h3 className="text-xl font-semibold mb-3">Read Aloud</h3>
            <p className="text-gray-600">Read sentences into the microphone and we'll check if you got it right.</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-5xl mb-4">⭐</div>
            <h3 className="text-xl font-semibold mb-3">Earn Points</h3>
            <p className="text-gray-600">Get points for every correct reading. The more you read, the more you earn!</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-5xl mb-4">🎁</div>
            <h3 className="text-xl font-semibold mb-3">Get Rewards</h3>
            <p className="text-gray-600">Trade your points for real rewards in the reward shop!</p>
          </div>
        </div>
      </div>
    </main>
  );
}
