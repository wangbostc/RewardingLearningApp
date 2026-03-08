import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/Nav';
import apiClient from '@/lib/api-client';
import type { ShopItem, AdminRedemption, AdminSentence } from '@/lib/api-client';

type Tab = 'redemptions' | 'rewards' | 'sentences';

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>('redemptions');
  const [redemptions, setRedemptions] = useState<AdminRedemption[]>([]);
  const [items, setItems] = useState<ShopItem[]>([]);
  const [sentences, setSentences] = useState<AdminSentence[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // New item form
  const [newItem, setNewItem] = useState({ name: '', description: '', emoji: '🎁', points_cost: 50 });
  const [showNewItem, setShowNewItem] = useState(false);

  useEffect(() => {
    const isAdmin = localStorage.getItem('isAdmin');
    if (isAdmin !== 'true') {
      navigate('/dashboard');
      return;
    }
    fetchAll();
  }, [navigate]);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [redData, itemData, sentData] = await Promise.all([
        apiClient.adminGetRedemptions(),
        apiClient.adminGetItems(),
        apiClient.adminGetSentences(),
      ]);
      setRedemptions(redData.redemptions || []);
      setItems(itemData.items || []);
      setSentences(sentData.sentences || []);
    } catch (err) {
      console.error('Admin fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (id: number, status: string) => {
    try {
      await apiClient.adminUpdateRedemption(id, status);
      setRedemptions((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status } : r))
      );
    } catch (err) {
      console.error('Update failed:', err);
    }
  };

  const handleCreateItem = async () => {
    try {
      await apiClient.adminCreateItem({
        ...newItem,
        is_active: true,
        id: 0,
      } as any);
      setShowNewItem(false);
      setNewItem({ name: '', description: '', emoji: '🎁', points_cost: 50 });
      const data = await apiClient.adminGetItems();
      setItems(data.items || []);
    } catch (err) {
      console.error('Create failed:', err);
    }
  };

  const handleDeleteItem = async (id: number) => {
    if (!confirm('Delete this reward item?')) return;
    try {
      await apiClient.adminDeleteItem(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleToggleItem = async (item: ShopItem) => {
    try {
      await apiClient.adminUpdateItem(item.id, { is_active: !item.is_active });
      setItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, is_active: !i.is_active } : i))
      );
    } catch (err) {
      console.error('Toggle failed:', err);
    }
  };

  const tabs: { key: Tab; label: string; icon: string }[] = [
    { key: 'redemptions', label: 'Redemptions', icon: '📋' },
    { key: 'rewards', label: 'Reward Items', icon: '🎁' },
    { key: 'sentences', label: 'Sentences', icon: '📝' },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <Nav showBack />

      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">⚙️ Admin Panel</h1>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-200 pb-2">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 rounded-t-lg font-semibold transition ${
                tab === t.key
                  ? 'bg-white text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : (
          <>
            {/* Redemptions Tab */}
            {tab === 'redemptions' && (
              <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <div className="p-4 border-b bg-gray-50">
                  <h2 className="font-bold text-gray-900">Pending Approvals</h2>
                </div>
                {redemptions.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">No redemptions yet</div>
                ) : (
                  <div className="divide-y">
                    {redemptions.map((r) => (
                      <div key={r.id} className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{r.reward_item_emoji || '🎁'}</span>
                          <div>
                            <p className="font-semibold text-gray-900">
                              {r.username} → {r.reward_item_name}
                            </p>
                            <p className="text-sm text-gray-500">
                              {r.points_spent} pts • {new Date(r.redeemed_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            r.status === 'fulfilled' ? 'bg-green-100 text-green-700' :
                            r.status === 'approved' ? 'bg-blue-100 text-blue-700' :
                            r.status === 'rejected' ? 'bg-red-100 text-red-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {r.status}
                          </span>
                          {r.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleStatusUpdate(r.id, 'approved')}
                                className="px-3 py-1 bg-green-500 text-white rounded-lg text-sm hover:bg-green-600"
                              >
                                ✅ Approve
                              </button>
                              <button
                                onClick={() => handleStatusUpdate(r.id, 'rejected')}
                                className="px-3 py-1 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600"
                              >
                                ❌ Reject
                              </button>
                            </>
                          )}
                          {r.status === 'approved' && (
                            <button
                              onClick={() => handleStatusUpdate(r.id, 'fulfilled')}
                              className="px-3 py-1 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600"
                            >
                              🎉 Fulfilled
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Reward Items Tab */}
            {tab === 'rewards' && (
              <div>
                <button
                  onClick={() => setShowNewItem(!showNewItem)}
                  className="mb-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  {showNewItem ? 'Cancel' : '+ Add Reward Item'}
                </button>

                {showNewItem && (
                  <div className="bg-white rounded-xl shadow-md p-6 mb-6">
                    <h3 className="font-bold text-gray-900 mb-4">New Reward Item</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <input
                        placeholder="Name"
                        value={newItem.name}
                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                        className="px-3 py-2 border rounded-lg text-gray-900"
                      />
                      <input
                        placeholder="Emoji (e.g. 🎁)"
                        value={newItem.emoji}
                        onChange={(e) => setNewItem({ ...newItem, emoji: e.target.value })}
                        className="px-3 py-2 border rounded-lg text-gray-900"
                      />
                      <input
                        placeholder="Description"
                        value={newItem.description}
                        onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                        className="px-3 py-2 border rounded-lg md:col-span-2 text-gray-900"
                      />
                      <input
                        type="number"
                        placeholder="Points Cost"
                        value={newItem.points_cost}
                        onChange={(e) => setNewItem({ ...newItem, points_cost: parseInt(e.target.value) || 0 })}
                        className="px-3 py-2 border rounded-lg text-gray-900"
                      />
                      <button
                        onClick={handleCreateItem}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                      >
                        Create Item
                      </button>
                    </div>
                  </div>
                )}

                <div className="bg-white rounded-xl shadow-md overflow-hidden">
                  <div className="divide-y">
                    {items.map((item) => (
                      <div key={item.id} className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{item.emoji || '🎁'}</span>
                          <div>
                            <p className="font-semibold text-gray-900">{item.name}</p>
                            <p className="text-sm text-gray-500">⭐ {item.points_cost} points</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleToggleItem(item)}
                            className={`px-3 py-1 rounded-lg text-sm ${
                              item.is_active
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-500'
                            }`}
                          >
                            {item.is_active ? '✅ Active' : '⏸️ Inactive'}
                          </button>
                          <button
                            onClick={() => handleDeleteItem(item.id)}
                            className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sentences Tab */}
            {tab === 'sentences' && (
              <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
                  <h2 className="font-bold text-gray-900">Reading Sentences ({sentences.length})</h2>
                </div>
                <div className="divide-y max-h-[600px] overflow-y-auto">
                  {sentences.map((s) => (
                    <div key={s.id} className="p-4 flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{s.text}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          📚 {s.lesson_title} • Level {s.difficulty_level} • ⭐ {s.points_value} pts
                        </p>
                      </div>
                      <button
                        onClick={async () => {
                          if (!confirm('Delete this sentence?')) return;
                          await apiClient.adminDeleteSentence(s.id);
                          setSentences((prev) => prev.filter((x) => x.id !== s.id));
                        }}
                        className="ml-4 px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200"
                      >
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}

