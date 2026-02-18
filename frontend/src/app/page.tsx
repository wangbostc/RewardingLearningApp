'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in (from localStorage)
    const userId = localStorage.getItem('userId');
    if (userId) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="text-2xl font-bold text-indigo-600">🎓 Learn English</div>
            <div className="flex gap-4">
              {isLoggedIn ? (
                <>
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
                  >
                    Dashboard
                  </button>
                  <button
                    onClick={() => {
                      localStorage.removeItem('userId');
                      localStorage.removeItem('username');
                      setIsLoggedIn(false);
                    }}
                    className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link href="/auth/login" className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50">
                    Login
                  </Link>
                  <Link href="/auth/register" className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Master English with Rewards!
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Learn English through engaging lessons, earn points and badges, and unlock achievements as you progress. Our adaptive system adjusts to your level.
          </p>

          {!isLoggedIn && (
            <div className="flex gap-4 justify-center">
              <Link
                href="/auth/register"
                className="px-8 py-4 rounded-lg bg-indigo-600 text-white text-lg font-semibold hover:bg-indigo-700 transition"
              >
                Get Started
              </Link>
              <Link
                href="/auth/login"
                className="px-8 py-4 rounded-lg border-2 border-indigo-600 text-indigo-600 text-lg font-semibold hover:bg-indigo-50 transition"
              >
                Login
              </Link>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-3">Adaptive Learning</h3>
            <p className="text-gray-600">
              Our system adapts to your learning pace and difficulty level, ensuring you stay challenged but not overwhelmed.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl mb-4">⭐</div>
            <h3 className="text-xl font-semibold mb-3">Earn Rewards</h3>
            <p className="text-gray-600">
              Complete lessons, earn points, unlock badges, and climb the leaderboard. Every achievement counts!
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-3">Track Progress</h3>
            <p className="text-gray-600">
              Monitor your learning journey with detailed statistics, streaks, and performance metrics.
            </p>
          </div>
        </div>
      </div>
    </main>
            <a
              href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
              className="font-medium text-zinc-950 dark:text-zinc-50"
            >
              Templates
            </a>{" "}
            or the{" "}
            <a
              href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
              className="font-medium text-zinc-950 dark:text-zinc-50"
            >
              Learning
            </a>{" "}
            center.
          </p>
        </div>
        <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
          <a
            className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-foreground px-5 text-background transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] md:w-[158px]"
            href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/vercel.svg"
              alt="Vercel logomark"
              width={16}
              height={16}
            />
            Deploy Now
          </a>
          <a
            className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-black/[.08] px-5 transition-colors hover:border-transparent hover:bg-black/[.04] dark:border-white/[.145] dark:hover:bg-[#1a1a1a] md:w-[158px]"
            href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Documentation
          </a>
        </div>
      </main>
    </div>
  );
}
