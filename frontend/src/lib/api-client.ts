const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      throw {
        status: response.status,
        ...data,
      };
    }

    return data;
  }

  // Auth endpoints
  async register(username: string, email: string, password: string, age?: number) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, age }),
    });
  }

  async login(username: string, password: string) {
    return this.request<{ id: number; username: string; is_admin?: boolean }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      }
    );
  }

  async getProfile(userId: number) {
    return this.request(`/auth/profile/${userId}`);
  }

  // Lesson endpoints
  async getLessons(difficulty?: string, category?: string) {
    const params = new URLSearchParams();
    if (difficulty) params.append('difficulty', difficulty);
    if (category) params.append('category', category);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<{ lessons: Lesson[] }>(`/lessons/${query}`);
  }

  async getLesson(lessonId: number) {
    return this.request(`/lessons/${lessonId}`);
  }

  // Speech / Reading endpoints
  async checkSpeech(userId: number, sentenceId: number, transcript: string) {
    return this.request<SpeechCheckResult>('/speech/check', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        sentence_id: sentenceId,
        transcript,
      }),
    });
  }

  async getNextSentence(userId: number) {
    return this.request<NextSentenceResult>(`/speech/next/${userId}`);
  }

  async getLessonSentences(lessonId: number) {
    return this.request<{ sentences: ReadingSentence[] }>(
      `/speech/sentences/${lessonId}`
    );
  }

  async recordReadingSuccess(userId: number, sentenceId: number) {
    return this.request(`/speech/record-success/${userId}/${sentenceId}`, {
      method: 'POST',
    });
  }

  // Progress endpoints
  async getUserProgress(userId: number) {
    return this.request<UserProgressData>(`/progress/user/${userId}`);
  }

  // Shop endpoints
  async getShopItems() {
    return this.request<{ items: ShopItem[] }>('/shop/items');
  }

  async redeemItem(itemId: number, userId: number) {
    return this.request(`/shop/redeem/${itemId}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  async getUserRedemptions(userId: number) {
    return this.request<{ redemptions: Redemption[] }>(
      `/shop/redemptions/${userId}`
    );
  }

  // Rewards endpoints
  async getUserAchievements(userId: number) {
    return this.request(`/rewards/achievements/${userId}`);
  }

  async checkAchievements(userId: number) {
    return this.request(`/rewards/check-achievements/${userId}`, {
      method: 'POST',
    });
  }

  // Admin endpoints
  async adminGetItems() {
    return this.request<{ items: ShopItem[] }>('/admin/shop/items');
  }

  async adminCreateItem(item: Omit<ShopItem, 'id'>) {
    return this.request('/admin/shop/items', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  async adminUpdateItem(itemId: number, item: Partial<ShopItem>) {
    return this.request(`/admin/shop/items/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    });
  }

  async adminDeleteItem(itemId: number) {
    return this.request(`/admin/shop/items/${itemId}`, {
      method: 'DELETE',
    });
  }

  async adminGetRedemptions(status?: string) {
    const query = status ? `?status_filter=${status}` : '';
    return this.request<{ redemptions: AdminRedemption[] }>(
      `/admin/redemptions${query}`
    );
  }

  async adminUpdateRedemption(redemptionId: number, status: string) {
    return this.request(`/admin/redemptions/${redemptionId}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async adminGetSentences() {
    return this.request<{ sentences: AdminSentence[] }>('/admin/sentences');
  }

  async adminCreateSentence(data: {
    lesson_id: number;
    text: string;
    difficulty_level: number;
    category: string;
    points_value: number;
    order?: number;
  }) {
    return this.request('/admin/sentences', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async adminDeleteSentence(sentenceId: number) {
    return this.request(`/admin/sentences/${sentenceId}`, {
      method: 'DELETE',
    });
  }

  async adminGetUsers() {
    return this.request('/admin/users');
  }
}

// Types
export interface Lesson {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  category: string;
  estimated_duration: number;
  exercise_count: number;
}

export interface ReadingSentence {
  id: number;
  text: string;
  difficulty_level: number;
  category: string;
  points_value: number;
  order: number;
  lesson_id?: number;
}

export type SpeechTokenStatus = 'correct' | 'wrong' | 'missing' | 'extra' | 'neutral';

export interface SpeechTokenFeedback {
  text: string;
  status: SpeechTokenStatus;
}

export interface SpeechCheckResult {
  is_correct: boolean;
  similarity: number;
  points_earned: number;
  expected: string;
  heard: string;
  message: string;
  expected_tokens: SpeechTokenFeedback[];
  heard_tokens: SpeechTokenFeedback[];
}

export interface NextSentenceResult {
  sentence: ReadingSentence | null;
  progress: {
    completed: number;
    total: number;
  };
  message?: string;
}

export interface UserProgressData {
  stats: {
    total_points: number;
    level: number;
    streak_days: number;
    total_lessons_completed: number;
    current_difficulty: string;
    accuracy_rate: number;
    last_activity?: string;
  };
  progress: Array<{
    lesson_id: number;
    lesson_title: string;
    status: string;
    progress_percentage: number;
    started_at: string;
    completed_at?: string;
  }>;
}

export interface ShopItem {
  id: number;
  name: string;
  description: string;
  image_url?: string;
  emoji?: string;
  points_cost: number;
  stock?: number;
  is_active: boolean;
}

export interface Redemption {
  id: number;
  user_id: number;
  reward_item_id: number;
  reward_item_name: string;
  reward_item_emoji?: string;
  points_spent: number;
  status: string;
  redeemed_at: string;
}

export interface AdminRedemption extends Redemption {
  username: string;
}

export interface AdminSentence {
  id: number;
  lesson_id: number;
  lesson_title: string;
  text: string;
  difficulty_level: number;
  category: string;
  points_value: number;
  order: number;
}

const apiClient = new ApiClient();
export default apiClient;

