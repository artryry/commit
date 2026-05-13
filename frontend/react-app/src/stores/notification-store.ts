import { create } from 'zustand';

/**
 * Элемент уведомления, полученный через WebSocket.
 */
export interface NotificationItem {
  id: string;
  type: string;        // chat.message | match.created | swipe.created
  message: string;
  senderId?: number;
  createdAt: string;    // ISO timestamp
}

interface NotificationState {
  items: NotificationItem[];
  unreadCount: number;

  /** Добавить новое уведомление */
  addNotification: (item: NotificationItem) => void;
  /** Сбросить счётчик непрочитанных (при открытии панели) */
  markAllRead: () => void;
  /** Очистить все уведомления */
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  items: [],
  unreadCount: 0,

  addNotification: (item) =>
    set((state) => ({
      items: [item, ...state.items].slice(0, 50), // keep last 50
      unreadCount: state.unreadCount + 1,
    })),

  markAllRead: () =>
    set({ unreadCount: 0 }),

  clearAll: () =>
    set({ items: [], unreadCount: 0 }),
}));
