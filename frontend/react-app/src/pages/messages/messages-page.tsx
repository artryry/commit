import { useState, useRef, useEffect, useCallback } from 'react';
import { useGetChats, useGetChatMessages, useSendMessage, useGetProfileById } from '@/api/hooks';
import { useAuthStore } from '@/stores/auth-store';
import type { ChatSummaryItem } from '@/api/hooks';

/**
 * MessagesPage — страница сообщений (список чатов + активный чат).
 */
export const MessagesPage = () => {
  const [selectedChat, setSelectedChat] = useState<ChatSummaryItem | null>(null);
  const [messageText, setMessageText] = useState('');
  const [isChatActive, setIsChatActive] = useState(false);

  const { data: chats, isLoading: chatsLoading } = useGetChats();
  const { data: chatData, refetch: refetchMessages } = useGetChatMessages(selectedChat?.peer_user_id ?? null);
  const sendMessageMutation = useSendMessage();
  const userId = useAuthStore((s) => s.userId);

  const messageAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Авто-прокрутка вниз при новых сообщениях
  useEffect(() => {
    if (messageAreaRef.current) {
      messageAreaRef.current.scrollTop = messageAreaRef.current.scrollHeight;
    }
  }, [chatData?.messages]);

  const handleSelectChat = useCallback((chat: ChatSummaryItem) => {
    setSelectedChat(chat);
    setIsChatActive(true);
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!messageText.trim() || !selectedChat) return;
    try {
      await sendMessageMutation.mutateAsync({
        peerUserId: selectedChat.peer_user_id,
        body: messageText.trim(),
      });
      setMessageText('');
      refetchMessages();
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch {
      // Handle silently
    }
  }, [messageText, selectedChat, sendMessageMutation, refetchMessages]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  };

  const formatDate = (isoString: string | null) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
    return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
  };

  if (chatsLoading) {
    return (
      <section className="message-page-container" style={{ display: 'flex' }}>
        <div style={{ margin: 'auto' }} className="animate-scale-in">
          <p style={{ color: 'var(--dark-color)', fontSize: 'var(--fs-24)' }}>Загрузка чатов...</p>
        </div>
      </section>
    );
  }

  return (
    <section className={`message-page-container ${isChatActive ? 'chat-active' : ''}`} style={{ display: 'flex' }}>
      {/* Chat List */}
      <section className="message-list glass-card">
        <div className="chat-option">
          {(chats || []).length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', opacity: 0.6 }}>
              <p style={{ fontSize: 'var(--fs-18)', color: 'var(--dark-color)' }}>
                У вас пока нет чатов
              </p>
              <p style={{ fontSize: 'var(--fs-12)', marginTop: '8px', color: 'var(--dark-color)' }}>
                Начните знакомиться, чтобы получить первый матч!
              </p>
            </div>
          ) : (
            (chats || []).map((chat) => (
              <ChatListItem
                key={chat.chat_id}
                chat={chat}
                isSelected={selectedChat?.chat_id === chat.chat_id}
                onClick={() => handleSelectChat(chat)}
                formatDate={formatDate}
              />
            ))
          )}
        </div>
      </section>

      {/* Chat Window */}
      <section className="message-chat glass-card">
        {selectedChat && chatData ? (
          <div className="chat">
            {/* Chat header */}
            <div className="profile-line">
              <button
                className="back-to-chats-btn"
                aria-label="Назад к чатам"
                onClick={() => setIsChatActive(false)}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
              </button>
              <div className="profile-line-img">
                <img src="/assets/photos/man_portret (4).png" alt="Фото профиля" />
              </div>
              <div className="profile-line-info">
                <h2 className="chat-name">Пользователь #{selectedChat.peer_user_id}</h2>
                <div className="second-line">
                  <span className="chat-status">{formatDate(chatData.messages?.[chatData.messages.length - 1]?.created_at ?? null)}</span>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="message-area" ref={messageAreaRef}>
              {(chatData.messages || []).map((msg) => (
                <div
                  key={msg.id}
                  className={`message ${msg.sender_id === userId ? 'outgoing' : 'incoming'}`}
                >
                  <div className="message-content">
                    {msg.body && <p>{msg.body}</p>}
                    <span className="message-time">{formatTime(msg.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Input field */}
            <div className="field">
              <div className="text-field">
                <div className="text-field-left-part">
                  <div className="emoji" title="Выбор эмодзи">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                      <line x1="9" y1="9" x2="9.01" y2="9" />
                      <line x1="15" y1="9" x2="15.01" y2="9" />
                    </svg>
                  </div>
                  <div className="text-field-input">
                    <textarea
                      ref={textareaRef}
                      rows={1}
                      placeholder="Сообщение"
                      maxLength={255}
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      onKeyDown={handleKeyDown}
                    />
                  </div>
                </div>
                <div className="text-field-right-part">
                  <div className="add-file" title="Вложения">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                    </svg>
                  </div>
                </div>
              </div>
              <div
                className="send-btn-container"
                title="Отправить сообщение"
                onClick={handleSendMessage}
                style={{ cursor: 'pointer' }}
              >
                <div className="send-btn">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div style={{ margin: 'auto', textAlign: 'center', opacity: 0.5 }}>
            <svg width="64" height="64" viewBox="0 0 32 32" fill="none" style={{ marginBottom: '16px' }}>
              <path d="M30 15.2222C30.0053 17.2754 29.5256 19.3007 28.6 21.1333C27.5024 23.3294 25.8151 25.1765 23.7271 26.4678C21.6391 27.7591 19.2328 28.4435 16.7778 28.4444C14.7246 28.4498 12.6993 27.9701 10.8667 27.0444L2 30L4.95555 21.1333C4.02989 19.3007 3.5502 17.2754 3.55555 15.2222C3.5565 12.7672 4.24095 10.3609 5.53222 8.27289C6.8235 6.18487 8.67061 4.49759 10.8667 3.40004C12.6993 2.47438 14.7246 1.99469 16.7778 2.00004H17.5555C20.7978 2.17892 23.8603 3.54745 26.1564 5.8436C28.4526 8.13974 29.8211 11.2022 30 14.4445V15.2222Z" stroke="var(--dark-color)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <p style={{ color: 'var(--dark-color)', fontSize: 'var(--fs-20)' }}>
              Выберите чат для начала общения
            </p>
          </div>
        )}
      </section>
    </section>
  );
};

/**
 * ChatListItem — одна строка в списке чатов.
 */
const ChatListItem = ({
  chat,
  isSelected,
  onClick,
  formatDate,
}: {
  chat: ChatSummaryItem;
  isSelected: boolean;
  onClick: () => void;
  formatDate: (d: string | null) => string;
}) => {
  return (
    <div
      className={`chat-profile-line ${isSelected ? 'picked' : ''}`}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      <div className="chat-profile-avatar">
        <img src="/assets/photos/man_portret (2).png" alt="Фото профиля" />
      </div>
      <div className="chat-profile-info">
        <div className="chat-profile-name">
          <span className="chat-profile-name-text">Пользователь #{chat.peer_user_id}</span>
          <span className="chat-profile-date">{formatDate(chat.last_message_at)}</span>
        </div>
        <div className="chat-profile-last-message">
          {chat.last_message_preview || 'Нет сообщений'}
        </div>
      </div>
    </div>
  );
};
