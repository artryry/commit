import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/auth-store';
import { useNotificationStore } from '@/stores/notification-store';

/**
 * Типы событий уведомлений, получаемых по WebSocket.
 */
export interface NotificationEvent {
  type: string;             // chat.message | match.created | swipe.created | chat.deleted
  message: string;
  chat_id?: string;
  message_id?: string;
  sender_id?: number;
  viewer_id?: number;
}

/** Человекочитаемый текст для типа уведомления */
function notificationLabel(type: string, message?: string): string {
  switch (type) {
    case 'chat.message':
      return message || 'Вам пришло новое сообщение';
    case 'match.created':
      return message || 'У вас новый коммит! 🎉';
    case 'swipe.created':
      return message || 'Кто-то оценил ваш профиль ❤️';
    case 'chat.deleted':
      return message || 'Чат был удалён';
    default:
      return message || 'Новое уведомление';
  }
}

/**
 * Хук подключения к WebSocket уведомлений.
 * Устанавливается после авторизации и автоматически
 * переподключается при обрыве соединения.
 */
export function useNotificationsWs() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const queryClient = useQueryClient();
  const addNotification = useNotificationStore((s) => s.addNotification);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!accessToken || !isAuthenticated) return;

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/api/v1/notifications/ws?token=${encodeURIComponent(accessToken)}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[NotificationsWS] connected');
    };

    ws.onmessage = (event) => {
      try {
        const data: NotificationEvent = JSON.parse(event.data);

        // Push into notification store for UI display
        addNotification({
          id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          type: data.type,
          message: notificationLabel(data.type, data.message),
          senderId: data.sender_id,
          createdAt: new Date().toISOString(),
        });

        // Invalidate relevant query caches
        switch (data.type) {
          case 'chat.message':
            queryClient.invalidateQueries({ queryKey: ['chats'] });
            if (data.sender_id) {
              queryClient.invalidateQueries({ queryKey: ['chats', data.sender_id] });
            }
            break;

          case 'match.created':
            queryClient.invalidateQueries({ queryKey: ['matches'] });
            queryClient.invalidateQueries({ queryKey: ['chats'] });
            break;

          case 'swipe.created':
            queryClient.invalidateQueries({ queryKey: ['swipes'] });
            break;

          case 'chat.deleted':
            queryClient.invalidateQueries({ queryKey: ['chats'] });
            break;

          default:
            break;
        }
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = (e) => {
      console.log('[NotificationsWS] disconnected', e.code);
      wsRef.current = null;
      // Reconnect after 3 seconds if still authenticated
      if (useAuthStore.getState().isAuthenticated) {
        reconnectTimer.current = setTimeout(connect, 3000);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [accessToken, isAuthenticated, queryClient, addNotification]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);
}
