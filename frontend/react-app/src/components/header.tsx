import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import { useNotificationStore } from '@/stores/notification-store';
import { useLogout, useGetMyProfile, useGetFilters, useSetFilters } from '@/api/hooks';
import { useQueryClient } from '@tanstack/react-query';
import type { RecommendationFilters } from '@/api/hooks';

const MINIO_PUBLIC_BASE = import.meta.env.VITE_MINIO_URL ?? 'http://localhost:9000';
function profileImageUrl(storageKey: string): string {
  const path = `profile/${storageKey}`.split('/').map(encodeURIComponent).join('/');
  return `${MINIO_PUBLIC_BASE.replace(/\/$/, '')}/${path}`;
}

export const SiteHeader = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const { items: notifications, unreadCount, markAllRead } = useNotificationStore();
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Filters
  const { data: savedFilters } = useGetFilters();
  const setFiltersMutation = useSetFilters();
  const [filterAgeFrom, setFilterAgeFrom] = useState(18);
  const [filterAgeTo, setFilterAgeTo] = useState(99);
  const [filterRelType, setFilterRelType] = useState('');
  const [filterGender, setFilterGender] = useState('');
  const [filterCity, setFilterCity] = useState('');
  const [filterSign, setFilterSign] = useState('');
  const [filterTags, setFilterTags] = useState<string[]>([]);
  const [filterTagInput, setFilterTagInput] = useState('');
  const [showFilterTagInput, setShowFilterTagInput] = useState(false);

  // Load saved filters into local state
  useEffect(() => {
    if (savedFilters) {
      setFilterAgeFrom(savedFilters.ageFrom ? Number(savedFilters.ageFrom) : 18);
      setFilterAgeTo(savedFilters.ageTo ? Number(savedFilters.ageTo) : 99);
      setFilterRelType(savedFilters.relationshipType || '');
      setFilterGender(savedFilters.partnerGender || '');
      setFilterCity(savedFilters.city || '');
      setFilterSign(savedFilters.sign || '');
      setFilterTags(savedFilters.tags || []);
    }
  }, [savedFilters]);

  const handleSaveFilters = useCallback(async () => {
    const body: RecommendationFilters = {
      ageFrom: String(filterAgeFrom),
      ageTo: String(filterAgeTo),
      relationshipType: filterRelType || undefined,
      partnerGender: filterGender || undefined,
      city: filterCity || undefined,
      sign: filterSign || undefined,
      tags: filterTags.length > 0 ? filterTags : undefined,
    };
    try {
      await setFiltersMutation.mutateAsync(body);
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      setShowFilters(false);
    } catch { /* ignore */ }
  }, [filterAgeFrom, filterAgeTo, filterRelType, filterGender, filterCity, filterSign, filterTags, setFiltersMutation, queryClient]);

  // Compute age slider percentage for background gradient
  const ageFromPct = ((filterAgeFrom - 18) / (99 - 18)) * 100;
  const ageToPct = ((filterAgeTo - 18) / (99 - 18)) * 100;

  const { refreshToken, logout: storeLogout } = useAuthStore();
  const logoutMutation = useLogout();
  const { data: profileData } = useGetMyProfile();
  const profile = profileData?.profile_data;

  const avatarSrc = profile?.avatar_image?.url
    ? profileImageUrl(profile.avatar_image.url)
    : '/assets/photos/man_portret (3).png';

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target as Node)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('click', handler);
    return () => document.removeEventListener('click', handler);
  }, []);

  const handleLogout = async () => {
    try {
      if (refreshToken) await logoutMutation.mutateAsync({ refresh_token: refreshToken });
    } finally {
      storeLogout();
      setShowLogoutModal(false);
      navigate('/poster');
    }
  };

  const isOnDiscover = location.pathname === '/discover';
  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      <header className="site-header">
        <div className="header-left">
          <a href="#" className="header-logo" aria-label="Commit" onClick={(e) => { e.preventDefault(); navigate('/profile'); }}>
            <img src="/assets/icons/Logo.png" alt="Логотип-Commit" />
          </a>
          <nav className="header-nav">
            {/* Уведомления */}
            <button className={`nav-icon-btn ${showNotifications ? 'nav-icon-btn--pink' : 'nav-icon-btn--yellow'}`} aria-label="Уведомления" onClick={() => { const next = !showNotifications; setShowNotifications(next); setShowFilters(false); if (next) markAllRead(); }}>
              {unreadCount > 0 && <span className="nav-notification-dot">{unreadCount > 9 ? '9+' : unreadCount}</span>}
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none"><path d="M24.9998 28.3333H33.3332L30.9916 25.9918C30.3566 25.3568 29.9998 24.4955 29.9998 23.5974V18.3333C29.9998 13.9793 27.2171 10.2751 23.3332 8.90236V8.33333C23.3332 6.49238 21.8408 5 19.9998 5C18.1589 5 16.6665 6.49238 16.6665 8.33333V8.90236C12.7825 10.2751 9.99984 13.9793 9.99984 18.3333V23.5974C9.99984 24.4955 9.64308 25.3568 9.00806 25.9918L6.6665 28.3333H14.9998M24.9998 28.3333V30C24.9998 32.7614 22.7613 35 19.9998 35C17.2384 35 14.9998 32.7614 14.9998 30V28.3333M24.9998 28.3333H14.9998" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            {/* Сообщения */}
            <button className={`nav-icon-btn ${isActive('/messages') ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} aria-label="Сообщения" onClick={() => navigate('/messages')}>
              <div className="open-button">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><path d="M30 15.2222C30.0053 17.2754 29.5256 19.3007 28.6 21.1333C27.5024 23.3294 25.8151 25.1765 23.7271 26.4678C21.6391 27.7591 19.2328 28.4435 16.7778 28.4444C14.7246 28.4498 12.6993 27.9701 10.8667 27.0444L2 30L4.95555 21.1333C4.02989 19.3007 3.5502 17.2754 3.55555 15.2222C3.5565 12.7672 4.24095 10.3609 5.53222 8.27289C6.8235 6.18487 8.67061 4.49759 10.8667 3.40004C12.6993 2.47438 14.7246 1.99469 16.7778 2.00004H17.5555C20.7978 2.17892 23.8603 3.54745 26.1564 5.8436C28.4526 8.13974 29.8211 11.2022 30 14.4445V15.2222Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                <span className="nav-btn-text">Сообщения</span>
              </div>
            </button>
            {/* Коммиты */}
            <button className={`nav-icon-btn ${isActive('/commits') ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} aria-label="Коммиты" onClick={() => navigate('/commits')}>
              <div className="open-button">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><path d="M3.25383 5.83802C0.337916 8.64418 0.337916 13.1939 3.25383 16L16.0003 28.2667L28.7466 16C31.6625 13.1939 31.6625 8.64418 28.7466 5.83802C25.8307 3.03186 21.1031 3.03186 18.1872 5.83802L16.0003 7.94272L13.8133 5.83802C10.8974 3.03186 6.16975 3.03186 3.25383 5.83802Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                <span className="nav-btn-text">Коммиты</span>
              </div>
            </button>
            {/* Знакомства */}
            <button className={`nav-icon-btn ${isActive('/discover') ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} aria-label="Знакомства" onClick={() => navigate('/discover')}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><g clipPath="url(#clip0_nav)"><path d="M13 32.0001C12.7812 32.0001 12.5687 31.9564 12.3687 31.8626C11.9875 31.6939 11.6937 31.3876 11.5437 30.9939L8.89372 24.1063L1.99996 21.4563C1.58746 21.3001 1.26246 20.9688 1.09996 20.5563C0.79371 19.7501 1.19371 18.8438 1.99996 18.5376L8.88747 15.8876L11.5437 9.00008C11.7 8.58757 12.0312 8.26257 12.4437 8.10007C12.8312 7.95007 13.2562 7.96257 13.6375 8.13132C14.0187 8.30007 14.3125 8.60632 14.4625 9.00008L17.1125 15.8876L24 18.5438C24.4125 18.7001 24.7375 19.0313 24.9 19.4438C25.2125 20.2501 24.8062 21.1563 24 21.4626L17.1125 24.1126L14.4562 31.0001C14.3 31.4126 13.9687 31.7376 13.5562 31.9001C13.3812 31.9689 13.1875 32.0001 13 32.0001Z" fill="currentColor" /><path d="M5.50001 11C5.08751 11 4.71251 10.7438 4.56876 10.3563L3.48126 7.51876L0.643751 6.43126C0.25625 6.28751 0 5.91251 0 5.50001C0 5.08751 0.25625 4.71251 0.643751 4.56876L3.48126 3.48126L4.56876 0.643751C4.71251 0.25625 5.08751 0 5.50001 0C5.91251 0 6.28751 0.25625 6.43126 0.643751L7.51876 3.48126L10.3563 4.56876C10.7438 4.71876 11 5.08751 11 5.50001C11 5.91251 10.7438 6.28751 10.3563 6.43126L7.51876 7.51876L6.43126 10.3563C6.28751 10.7438 5.91251 11 5.50001 11Z" fill="currentColor" /><path d="M25 16C24.5875 16 24.2125 15.7438 24.0688 15.3563L22.5625 11.4375L18.6438 9.93126C18.2562 9.78126 18 9.41251 18 9.00001C18 8.58751 18.2562 8.21251 18.6438 8.06876L22.5625 6.56251L24.0688 2.64375C24.2188 2.25625 24.5875 2 25 2C25.4125 2 25.7875 2.25625 25.9313 2.64375L27.4375 6.56251L31.3563 8.06876C31.7438 8.21876 32 8.58751 32 9.00001C32 9.41251 31.7438 9.78751 31.3563 9.93126L27.4375 11.4375L25.9313 15.3563C25.7875 15.7438 25.4125 16 25 16Z" fill="currentColor" /></g><defs><clipPath id="clip0_nav"><rect width="32" height="32" fill="white" /></clipPath></defs></svg>
              <span className="nav-btn-text">Знакомства</span>
            </button>
            {/* Фильтр — только на странице Знакомства */}
            {isOnDiscover && (
              <button className={`nav-icon-btn ${showFilters ? 'nav-icon-btn--pink' : 'nav-icon-btn--yellow'}`} aria-label="Фильтр" onClick={() => { setShowFilters(!showFilters); setShowNotifications(false); }}>
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none"><path d="M19.9998 9.99984V6.6665M19.9998 9.99984C18.1589 9.99984 16.6665 11.4922 16.6665 13.3332C16.6665 15.1741 18.1589 16.6665 19.9998 16.6665M19.9998 9.99984C21.8408 9.99984 23.3332 11.4922 23.3332 13.3332C23.3332 15.1741 21.8408 16.6665 19.9998 16.6665M9.99984 29.9998C11.8408 29.9998 13.3332 28.5075 13.3332 26.6665C13.3332 24.8256 11.8408 23.3332 9.99984 23.3332M9.99984 29.9998C8.15889 29.9998 6.6665 28.5075 6.6665 26.6665C6.6665 24.8256 8.15889 23.3332 9.99984 23.3332M9.99984 29.9998V33.3332M9.99984 23.3332V6.6665M19.9998 16.6665V33.3332M29.9998 29.9998C31.8408 29.9998 33.3332 28.5075 33.3332 26.6665C33.3332 24.8256 31.8408 23.3332 29.9998 23.3332M29.9998 29.9998C28.1589 29.9998 26.6665 28.5075 26.6665 26.6665C26.6665 24.8256 28.1589 23.3332 29.9998 23.3332M29.9998 29.9998V33.3332M29.9998 23.3332V6.6665" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </button>
            )}
          </nav>
        </div>
        <div className="header-right">
          <div className="header-user">
            <button className={`nav-icon-btn ${showNotifications ? 'nav-icon-btn--pink' : 'nav-icon-btn--yellow'}`} aria-label="Уведомления" onClick={() => { const next = !showNotifications; setShowNotifications(next); setShowFilters(false); if (next) markAllRead(); }}>
              {unreadCount > 0 && <span className="nav-notification-dot">{unreadCount > 9 ? '9+' : unreadCount}</span>}
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none"><path d="M24.9998 28.3333H33.3332L30.9916 25.9918C30.3566 25.3568 29.9998 24.4955 29.9998 23.5974V18.3333C29.9998 13.9793 27.2171 10.2751 23.3332 8.90236V8.33333C23.3332 6.49238 21.8408 5 19.9998 5C18.1589 5 16.6665 6.49238 16.6665 8.33333V8.90236C12.7825 10.2751 9.99984 13.9793 9.99984 18.3333V23.5974C9.99984 24.4955 9.64308 25.3568 9.00806 25.9918L6.6665 28.3333H14.9998M24.9998 28.3333V30C24.9998 32.7614 22.7613 35 19.9998 35C17.2384 35 14.9998 32.7614 14.9998 30V28.3333M24.9998 28.3333H14.9998" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            <div className="header-profile-menu-container" ref={profileMenuRef} style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 'inherit', cursor: 'pointer' }} onClick={() => setShowProfileMenu(!showProfileMenu)}>
              <img src={avatarSrc} alt="Аватар" className="header-user-avatar" />
              <span className="header-user-name">{profile?.username || 'Пользователь'}</span>
              {showProfileMenu && (
                <div className="chat-dropdown-menu" style={{ display: 'flex' }}>
                  <button className="chat-dropdown-item" onClick={(e) => { e.stopPropagation(); navigate('/profile'); setShowProfileMenu(false); }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                    Профиль
                  </button>
                  <button className="chat-dropdown-item danger" onClick={(e) => { e.stopPropagation(); setShowProfileMenu(false); setShowLogoutModal(true); }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
                    Выйти из профиля
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Notification Menu */}
      {showNotifications && (
        <div className="notification-menu" onClick={() => setShowNotifications(false)}>
          <h2 className="notification-header">Уведомления</h2>
          <div className="notification-list">
            {notifications.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px 12px', opacity: 0.5 }}>
                <p style={{ fontSize: 'var(--fs-18)', color: 'var(--dark-color)' }}>Нет уведомлений</p>
              </div>
            ) : (
              notifications.map((n) => (
                <div className="chat-profile-line" key={n.id}>
                  <div className="chat-profile-avatar">
                    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" style={{ padding: '6px' }}>
                      {n.type === 'chat.message' && <path d="M30 15.22C30.01 17.28 29.53 19.3 28.6 21.13C27.5 23.33 25.82 25.18 23.73 26.47C21.64 27.76 19.23 28.44 16.78 28.44C14.72 28.45 12.7 27.97 10.87 27.04L2 30L4.96 21.13C4.03 19.3 3.55 17.28 3.56 15.22C3.56 12.77 4.24 10.36 5.53 8.27C6.82 6.18 8.67 4.5 10.87 3.4C12.7 2.47 14.72 1.99 16.78 2H17.56C20.8 2.18 23.86 3.55 26.16 5.84C28.45 8.14 29.82 11.2 30 14.44V15.22Z" stroke="var(--main-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />}
                      {n.type === 'match.created' && <path d="M3.25 5.84C0.34 8.64 0.34 13.19 3.25 16L16 28.27L28.75 16C31.66 13.19 31.66 8.64 28.75 5.84C25.83 3.03 21.1 3.03 18.19 5.84L16 7.94L13.81 5.84C10.9 3.03 6.17 3.03 3.25 5.84Z" stroke="var(--supper-accent-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" transform="translate(4,6) scale(0.85)" />}
                      {n.type === 'swipe.created' && <path d="M20 6L22.47 13.53L30 16L22.47 18.47L20 26L17.53 18.47L10 16L17.53 13.53L20 6Z" stroke="var(--accent-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="var(--accent-color)" fillOpacity="0.2" />}
                      {!['chat.message','match.created','swipe.created'].includes(n.type) && <circle cx="20" cy="20" r="12" stroke="var(--dark-color)" strokeWidth="2" />}
                    </svg>
                  </div>
                  <div className="chat-profile-info">
                    <div className="chat-profile-name">
                      <span className="chat-profile-name-text">{n.type === 'chat.message' ? 'Сообщение' : n.type === 'match.created' ? 'Коммит' : n.type === 'swipe.created' ? 'Лайк' : 'Уведомление'}</span>
                      <span className="chat-profile-date">{new Date(n.createdAt).toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' })}</span>
                    </div>
                    <div className="chat-profile-last-message">{n.message}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Filter Menu */}
      {showFilters && (
        <div className="filter-menu" onClick={(e) => e.stopPropagation()}>
          <h2 className="notification-header">Фильтры</h2>
          <div className="filters">
            {/* Возраст от */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Возраст от</label></div>
              <div className="filter-item-bottom" style={{ position: 'relative', paddingTop: '24px' }}>
                <span className="age-value" style={{ position: 'absolute', top: 0, left: `${ageFromPct}%`, transform: 'translateX(-50%)', fontWeight: 600, fontSize: 'var(--fs-18)', color: 'var(--dark-color)' }}>{filterAgeFrom}</span>
                <input type="range" className="custom-range" value={filterAgeFrom} min={18} max={99} style={{ background: `linear-gradient(to right, var(--accent-color) ${ageFromPct}%, #F2EED9 ${ageFromPct}%)` }} onChange={(e) => { const v = Number(e.target.value); setFilterAgeFrom(v > filterAgeTo ? filterAgeTo : v); }} />
              </div>
            </div>
            {/* Возраст до */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Возраст до</label></div>
              <div className="filter-item-bottom" style={{ position: 'relative', paddingTop: '24px' }}>
                <span className="age-value" style={{ position: 'absolute', top: 0, left: `${ageToPct}%`, transform: 'translateX(-50%)', fontWeight: 600, fontSize: 'var(--fs-18)', color: 'var(--dark-color)' }}>{filterAgeTo}</span>
                <input type="range" className="custom-range" value={filterAgeTo} min={18} max={99} style={{ background: `linear-gradient(to right, var(--accent-color) ${ageToPct}%, #F2EED9 ${ageToPct}%)` }} onChange={(e) => { const v = Number(e.target.value); setFilterAgeTo(v < filterAgeFrom ? filterAgeFrom : v); }} />
              </div>
            </div>
            {/* Тип отношений */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Ищу</label></div>
              <div className="filter-item-bottom">
                <select className="filter-select" value={filterRelType} onChange={(e) => setFilterRelType(e.target.value)}>
                  <option value="">Любой</option>
                  <option value="RELATIONSHIP">Партнёра</option>
                  <option value="FRIENDSHIP">Друга</option>
                  <option value="UNSPECIFIED">Неопределено</option>
                </select>
              </div>
            </div>
            {/* Пол */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Пол</label></div>
              <div className="filter-item-bottom">
                <select className="filter-select" value={filterGender} onChange={(e) => setFilterGender(e.target.value)}>
                  <option value="">Любой</option>
                  <option value="MALE">Мужской</option>
                  <option value="FEMALE">Женский</option>
                </select>
              </div>
            </div>
            {/* Город */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Город</label></div>
              <div className="filter-item-bottom">
                <input type="text" className="filter-select" placeholder="Например: Москва" value={filterCity} onChange={(e) => setFilterCity(e.target.value)} />
              </div>
            </div>
            {/* Знак зодиака */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Знак зодиака</label></div>
              <div className="filter-item-bottom">
                <select className="filter-select" value={filterSign} onChange={(e) => setFilterSign(e.target.value)}>
                  <option value="">Любой</option>
                  <option value="ARIES">Овен</option>
                  <option value="TAURUS">Телец</option>
                  <option value="GEMINI">Близнецы</option>
                  <option value="CANCER">Рак</option>
                  <option value="LEO">Лев</option>
                  <option value="VIRGO">Дева</option>
                  <option value="LIBRA">Весы</option>
                  <option value="SCORPIO">Скорпион</option>
                  <option value="SAGITTARIUS">Стрелец</option>
                  <option value="CAPRICORN">Козерог</option>
                  <option value="AQUARIUS">Водолей</option>
                  <option value="PISCES">Рыбы</option>
                </select>
              </div>
            </div>
            {/* Теги */}
            <div className="filter-item">
              <div className="filter-item-top"><label>Теги</label></div>
              <div className="filter-item-bottom">
                <div className="interests-container">
                  {filterTags.map((tag, i) => (
                    <span className="interest-tag" key={i} onClick={() => setFilterTags((prev) => prev.filter((_, idx) => idx !== i))} style={{ cursor: 'pointer' }} title="Нажмите чтобы удалить">#{tag}</span>
                  ))}
                  {showFilterTagInput ? (
                    <span className="interest-tag" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      #<input type="text" value={filterTagInput} onChange={(e) => setFilterTagInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); const v = filterTagInput.trim(); if (v && !filterTags.includes(v)) setFilterTags((p) => [...p, v]); setFilterTagInput(''); setShowFilterTagInput(false); } if (e.key === 'Escape') setShowFilterTagInput(false); }} onBlur={() => { const v = filterTagInput.trim(); if (v && !filterTags.includes(v)) setFilterTags((p) => [...p, v]); setFilterTagInput(''); setShowFilterTagInput(false); }} autoFocus style={{ border: 'none', background: 'transparent', fontFamily: 'inherit', fontSize: 'inherit', outline: 'none', width: '80px' }} />
                    </span>
                  ) : (
                    <button className="interest-add-btn" aria-label="Добавить тег" onClick={() => setShowFilterTagInput(true)}>
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1V8M8 8V15M8 8H15M8 8H1" stroke="#FF5777" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    </button>
                  )}
                </div>
              </div>
            </div>
            {/* Кнопка сохранения */}
            <button className="poster-button" onClick={handleSaveFilters} style={{ marginTop: '8px' }}>
              {setFiltersMutation.isPending ? 'Сохранение...' : 'Применить'}
            </button>
          </div>
        </div>
      )}

      {/* Mobile Bottom Nav */}
      <nav className="mobile-bottom-nav">
        <div className="btm-btn-container">
          <div className="btn-list">
            <button className={`nav-icon-btn ${isActive('/messages') ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} onClick={() => navigate('/messages')}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><path d="M30 15.2222C30.0053 17.2754 29.5256 19.3007 28.6 21.1333C27.5024 23.3294 25.8151 25.1765 23.7271 26.4678C21.6391 27.7591 19.2328 28.4435 16.7778 28.4444C14.7246 28.4498 12.6993 27.9701 10.8667 27.0444L2 30L4.95555 21.1333C4.02989 19.3007 3.5502 17.2754 3.55555 15.2222C3.5565 12.7672 4.24095 10.3609 5.53222 8.27289C6.8235 6.18487 8.67061 4.49759 10.8667 3.40004C12.6993 2.47438 14.7246 1.99469 16.7778 2.00004H17.5555C20.7978 2.17892 23.8603 3.54745 26.1564 5.8436C28.4526 8.13974 29.8211 11.2022 30 14.4445V15.2222Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            <button className={`nav-icon-btn ${isActive('/commits') ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} onClick={() => navigate('/commits')}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><path d="M3.25383 5.83802C0.337916 8.64418 0.337916 13.1939 3.25383 16L16.0003 28.2667L28.7466 16C31.6625 13.1939 31.6625 8.64418 28.7466 5.83802C25.8307 3.03186 21.1031 3.03186 18.1872 5.83802L16.0003 7.94272L13.8133 5.83802C10.8974 3.03186 6.16975 3.03186 3.25383 5.83802Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            <button className={`nav-icon-btn ${isActive('/discover') ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} onClick={() => navigate('/discover')}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><g clipPath="url(#clip0_mob)"><path d="M13 32.0001C12.7812 32.0001 12.5687 31.9564 12.3687 31.8626C11.9875 31.6939 11.6937 31.3876 11.5437 30.9939L8.89372 24.1063L1.99996 21.4563C1.58746 21.3001 1.26246 20.9688 1.09996 20.5563C0.79371 19.7501 1.19371 18.8438 1.99996 18.5376L8.88747 15.8876L11.5437 9.00008C11.7 8.58757 12.0312 8.26257 12.4437 8.10007C12.8312 7.95007 13.2562 7.96257 13.6375 8.13132C14.0187 8.30007 14.3125 8.60632 14.4625 9.00008L17.1125 15.8876L24 18.5438C24.4125 18.7001 24.7375 19.0313 24.9 19.4438C25.2125 20.2501 24.8062 21.1563 24 21.4626L17.1125 24.1126L14.4562 31.0001C14.3 31.4126 13.9687 31.7376 13.5562 31.9001C13.3812 31.9689 13.1875 32.0001 13 32.0001Z" fill="currentColor" /><path d="M5.50001 11C5.08751 11 4.71251 10.7438 4.56876 10.3563L3.48126 7.51876L0.643751 6.43126C0.25625 6.28751 0 5.91251 0 5.50001C0 5.08751 0.25625 4.71251 0.643751 4.56876L3.48126 3.48126L4.56876 0.643751C4.71251 0.25625 5.08751 0 5.50001 0C5.91251 0 6.28751 0.25625 6.43126 0.643751L7.51876 3.48126L10.3563 4.56876C10.7438 4.71876 11 5.08751 11 5.50001C11 5.91251 10.7438 6.28751 10.3563 6.43126L7.51876 7.51876L6.43126 10.3563C6.28751 10.7438 5.91251 11 5.50001 11Z" fill="currentColor" /><path d="M25 16C24.5875 16 24.2125 15.7438 24.0688 15.3563L22.5625 11.4375L18.6438 9.93126C18.2562 9.78126 18 9.41251 18 9.00001C18 8.58751 18.2562 8.21251 18.6438 8.06876L22.5625 6.56251L24.0688 2.64375C24.2188 2.25625 24.5875 2 25 2C25.4125 2 25.7875 2.25625 25.9313 2.64375L27.4375 6.56251L31.3563 8.06876C31.7438 8.21876 32 8.58751 32 9.00001C32 9.41251 31.7438 9.78751 31.3563 9.93126L27.4375 11.4375L25.9313 15.3563C25.7875 15.7438 25.4125 16 25 16Z" fill="currentColor" /></g><defs><clipPath id="clip0_mob"><rect width="32" height="32" fill="white" /></clipPath></defs></svg>
            </button>
            {isOnDiscover && (
              <button className={`nav-icon-btn ${showFilters ? 'nav-icon-btn--pink active' : 'nav-icon-btn--yellow'}`} aria-label="Фильтр" onClick={() => { setShowFilters(!showFilters); setShowNotifications(false); }}>
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none"><path d="M19.9998 9.99984V6.6665M19.9998 9.99984C18.1589 9.99984 16.6665 11.4922 16.6665 13.3332C16.6665 15.1741 18.1589 16.6665 19.9998 16.6665M19.9998 9.99984C21.8408 9.99984 23.3332 11.4922 23.3332 13.3332C23.3332 15.1741 21.8408 16.6665 19.9998 16.6665M9.99984 29.9998C11.8408 29.9998 13.3332 28.5075 13.3332 26.6665C13.3332 24.8256 11.8408 23.3332 9.99984 23.3332M9.99984 29.9998C8.15889 29.9998 6.6665 28.5075 6.6665 26.6665C6.6665 24.8256 8.15889 23.3332 9.99984 23.3332M9.99984 29.9998V33.3332M9.99984 23.3332V6.6665M19.9998 16.6665V33.3332M29.9998 29.9998C31.8408 29.9998 33.3332 28.5075 33.3332 26.6665C33.3332 24.8256 31.8408 23.3332 29.9998 23.3332M29.9998 29.9998C28.1589 29.9998 26.6665 28.5075 26.6665 26.6665C26.6665 24.8256 28.1589 23.3332 29.9998 23.3332M29.9998 29.9998V33.3332M29.9998 23.3332V6.6665" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Logout Modal */}
      {showLogoutModal && (
        <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) setShowLogoutModal(false); }}>
          <div className="modal-content glass-card-inner">
            <h2 className="modal-title">Вы точно хотите выйти?</h2>
            <div className="modal-buttons">
              <button className="btn-modal btn-modal--yes" onClick={handleLogout}>Да</button>
              <button className="btn-modal btn-modal--no" onClick={() => setShowLogoutModal(false)}>Нет</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
