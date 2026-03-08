import { Link, useNavigate } from 'react-router-dom';

interface NavProps {
  showBack?: boolean;
  backTo?: string;
  backLabel?: string;
}

export default function Nav({ showBack, backTo = '/dashboard', backLabel = 'Dashboard' }: NavProps) {
  const navigate = useNavigate();
  const username = localStorage.getItem('username');
  const isLoggedIn = !!localStorage.getItem('userId');

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    localStorage.removeItem('isAdmin');
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <Link to={isLoggedIn ? '/dashboard' : '/'} className="text-2xl font-bold text-indigo-600">
            🎓 Learn English
          </Link>
          <div className="flex items-center gap-4">
            {showBack && (
              <Link to={backTo} className="text-indigo-600 hover:text-indigo-700">
                ← {backLabel}
              </Link>
            )}
            {isLoggedIn && (
              <>
                <span className="text-gray-700 hidden sm:inline">Hi, {username}!</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

