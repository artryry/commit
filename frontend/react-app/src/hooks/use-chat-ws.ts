import { useEffect, useRef, useCallback, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/auth-store';
import type { ChatMessageItem } from '@/api/hooks';

/**
 * Типы сообщений, получаемых с chat WS.
 */
interface ChatWsNewMessage {
  type: 'chat.new_message';
  chat_id: string;
  message: ChatMessageItem;
}

interface ChatWsError {
  type: 'error';
  detail: string;
}

type ChatWsEvent = ChatWsNewMessage | ChatWsError;

/**
 * Хук подключения к WebSocket конкретного чата.
 * Устанавливает соединение при выборе чата,
 * обрабатывает входящие сообщения, и предоставляет метод отправки.
 */
export function useChatWs(peerUserId: number | null) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    if (!peerUserId || !accessToken) return;

    // Close previous connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/api/v1/chats/${peerUserId}/ws?token=${encodeURIComponent(accessToken)}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`[ChatWS:${peerUserId}] connected`);
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data: ChatWsEvent = JSON.parse(event.data);

        if (data.type === 'chat.new_message') {
          // Append message to chat query cache
          queryClient.invalidateQueries({ queryKey: ['chats', peerUserId] });
          queryClient.invalidateQueries({ queryKey: ['chats'] });
        }
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      console.log(`[ChatWS:${peerUserId}] disconnected`);
      wsRef.current = null;
      setConnected(false);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [peerUserId, accessToken, queryClient]);

  // Send a text message via WebSocket
  const sendWsMessage = useCallback((body: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'text', body }));
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return { connected, sendWsMessage };
}
