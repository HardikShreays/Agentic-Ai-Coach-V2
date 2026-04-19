import { create } from 'zustand';

import type { AuthUser } from '../api/client';
import { getMe, login as apiLogin, logout as apiLogout, signup as apiSignup } from '../api/client';

type AuthStore = {
  user: AuthUser | null;
  isLoading: boolean;
  setUser: (u: AuthUser | null) => void;
  refreshMe: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isLoading: false,
  setUser: (u) => set({ user: u }),

  refreshMe: async () => {
    set({ isLoading: true });
    try {
      const me = await getMe();
      set({ user: me });
    } catch {
      set({ user: null });
    } finally {
      set({ isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const u = await apiLogin({ email, password });
      set({ user: u });
    } finally {
      set({ isLoading: false });
    }
  },

  signup: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const u = await apiSignup({ email, password });
      set({ user: u });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await apiLogout();
    } finally {
      set({ user: null, isLoading: false });
    }
  },
}));

