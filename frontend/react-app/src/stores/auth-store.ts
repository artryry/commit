import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

/**
 * Интерфейс состояния аутентификации.
 * Хранит токены и базовую информацию о пользователе.
 */
interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  userId: number | null;
  isAuthenticated: boolean;
  hasProfile: boolean;

  // Actions
  setTokens: (accessToken: string, refreshToken: string) => void;
  setAccessToken: (accessToken: string) => void;
  setUserId: (userId: number) => void;
  setHasProfile: (hasProfile: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      userId: null,
      isAuthenticated: false,
      hasProfile: false,

      setTokens: (accessToken, refreshToken) =>
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
        }),

      setAccessToken: (accessToken) =>
        set({ accessToken }),

      setUserId: (userId) =>
        set({ userId }),

      setHasProfile: (hasProfile) =>
        set({ hasProfile }),

      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          userId: null,
          isAuthenticated: false,
          hasProfile: false,
        }),
    }),
    {
      name: 'commit-auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        userId: state.userId,
        isAuthenticated: state.isAuthenticated,
        hasProfile: state.hasProfile,
      }),
    },
  ),
);
