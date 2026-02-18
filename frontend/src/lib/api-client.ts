const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
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
  async register(username: string, email: string, password: string, age?: number, nativeLanguage?: string) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username,
        email,
        password,
        age,
        native_language: nativeLanguage,
      }),
    });
  }

  async login(username: string, password: string) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async getProfile(userId: number) {
    return this.request(`/auth/profile/${userId}`);
  }

  // Lesson endpoints
  async getLessons(difficulty?: string, category?: string) {
    let query = '';
    const params = new URLSearchParams();
    if (difficulty) params.append('difficulty', difficulty);
    if (category) params.append('category', category);
    if (params.toString()) query = `?${params.toString()}`;

    return this.request(`/lessons${query}`);
  }

  async getLesson(lessonId: number) {
    return this.request(`/lessons/${lessonId}`);
  }

  async getLessonProgress(userId: number, lessonId: number) {
    return this.request(`/lessons/${userId}/progress/${lessonId}`);
  }

  async startLesson(userId: number, lessonId: number) {
    return this.request(`/lessons/${userId}/start/${lessonId}`, {
      method: 'POST',
    });
  }

  // Progress endpoints
  async submitExercise(userId: number, exerciseId: number, answer: any, timeSpent?: number) {
    return this.request(`/progress/exercises/${userId}/${exerciseId}`, {
      method: 'POST',
      body: JSON.stringify({
        answer,
        time_spent: timeSpent,
      }),
    });
  }

  async getUserProgress(userId: number) {
    return this.request(`/progress/user/${userId}`);
  }

  async completeLesson(userId: number, lessonId: number) {
    return this.request(`/progress/lessons/${lessonId}/complete/${userId}`, {
      method: 'POST',
    });
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

  async getLeaderboard(limit: number = 10) {
    return this.request(`/rewards/leaderboard?limit=${limit}`);
  }

  async getUserRewards(userId: number, limit: number = 20) {
    return this.request(`/rewards/user/${userId}/rewards?limit=${limit}`);
  }
}

export default new ApiClient();

