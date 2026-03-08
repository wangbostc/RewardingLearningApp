import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type { ShopItem, Redemption } from '@/lib/api-client';

export default function ShopPage() {
  const [items, setItems] = useState<ShopItem[]>([]);
  const [redemptions, setRedemptions] = useState<Redemption[]>([]);
  const [points, setPoints] = useState(0);
  const [loading, setLoading] = useState(true);
  const [redeemingId, setRedeemingId] = useState<number | null>(null);
  const [message, setMessage] = useState('');
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
      const [shopData, progressData, redemptionData] = await Promise.all([
        apiClient.getShopItems(),
        apiClient.getUserProgress(parseInt(userId!)),
        apiClient.getUserRedemptions(parseInt(userId!)),
      ]);
      setItems(shopData.items || []);
      setPoints(progressData.stats.total_points);
      setRedemptions(redemptionData.redemptions || []);
    } catch (err) {
      console.error('Failed to load shop:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async (item: ShopItem) => {
    if (!userId) return;
    setRedeemingId(item.id);
    setMessage('');

    try {
      const res = await apiClient.redeemItem(item.id, parseInt(userId)) as any;
      setMessage(res.message || `Redeemed "${item.name}"!`);
      setPoints(res.redemption?.remaining_points ?? points - item.points_cost);
      // Refresh redemptions
      const redemptionData = await apiClient.getUserRedemptions(parseInt(userId));
      setRedemptions(redemptionData.redemptions || []);
    } catch (err: any) {
      setMessage(err.detail || 'Failed to redeem. Try again.');
    } finally {
      setRedeemingId(null);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
        <Nav showBack />
        <div className="flex items-center justify-center h-96">
          <div className="text-xl text-gray-600">Loading shop...</div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      <Nav showBack />

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Points Balance */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8 text-center">
          <p className="text-sm text-gray-500 mb-1">Your Points Balance</p>
          <p className="text-5xl font-bold text-indigo-600">⭐ {points}</p>
        </div>

        {message && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 text-center font-semibold">
            {message}
          </div>
        )}

        <h1 className="text-3xl font-bold text-gray-900 mb-6">🎁 Reward Shop</h1>

        {/* Shop Items Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {items.map((item) => {
            const canAfford = points >= item.points_cost;
            return (
              <div key={item.id} className="bg-white rounded-xl shadow-md p-6 flex flex-col">
                <div className="text-5xl text-center mb-3">{item.emoji || '🎁'}</div>
                <h3 className="text-lg font-bold text-gray-900 text-center mb-2">{item.name}</h3>
                <p className="text-sm text-gray-500 text-center mb-4 flex-grow">{item.description}</p>
                <div className="text-center mb-3">
                  <span className="text-lg font-bold text-indigo-600">⭐ {item.points_cost}</span>
                </div>
                <button
                  onClick={() => handleRedeem(item)}
                  disabled={!canAfford || redeemingId === item.id}
                  className={`w-full py-3 rounded-lg font-semibold transition ${
                    canAfford
                      ? 'bg-purple-500 text-white hover:bg-purple-600'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {redeemingId === item.id
                    ? 'Redeeming...'
                    : canAfford
                    ? 'Redeem 🎁'
                    : `Need ${item.points_cost - points} more`}
                </button>
              </div>
            );
          })}
        </div>

        {/* Redemption History */}
        {redemptions.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">My Redemptions</h2>
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              {redemptions.map((r) => (
                <div key={r.id} className="flex items-center justify-between p-4 border-b border-gray-100 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{r.reward_item_emoji || '🎁'}</span>
                    <div>
                      <p className="font-semibold text-gray-900">{r.reward_item_name}</p>
                      <p className="text-sm text-gray-500">{new Date(r.redeemed_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    r.status === 'fulfilled' ? 'bg-green-100 text-green-700' :
                    r.status === 'approved' ? 'bg-blue-100 text-blue-700' :
                    r.status === 'rejected' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {r.status === 'pending' ? '⏳ Waiting for Mum/Dad' :
                     r.status === 'approved' ? '✅ Approved' :
                     r.status === 'fulfilled' ? '🎉 Done!' :
                     '❌ Rejected'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

