import { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import { useLogout, useGetMyProfile } from '@/api/hooks';

/**
 * SiteHeader — основной заголовок приложения.
 * Содержит навигацию, уведомления, профиль пользователя и модальное окно выхода.
 */
export const SiteHeader = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [activeNav, setActiveNav] = useState<string | null>(null);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  const { refreshToken, logout: storeLogout } = useAuthStore();
  const logoutMutation = useLogout();
  const { data: profileData } = useGetMyProfile();

  const profile = profileData?.profile_data;

  // Закрытие меню при клике вне
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
      if (refreshToken) {
        await logoutMutation.mutateAsync({ refresh_token: refreshToken });
      }
    } finally {
      storeLogout();
      setShowLogoutModal(false);
      navigate('/poster');
    }
  };

  const handleNavClick = (navId: string, path: string) => {
    setActiveNav(activeNav === navId ? null : navId);
    navigate(path);
  };

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
            <button className="nav-icon-btn nav-icon-btn--yellow" aria-label="Уведомления">
              <span className="nav-notification-dot">2</span>
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M24.9998 28.3333H33.3332L30.9916 25.9918C30.3566 25.3568 29.9998 24.4955 29.9998 23.5974V18.3333C29.9998 13.9793 27.2171 10.2751 23.3332 8.90236V8.33333C23.3332 6.49238 21.8408 5 19.9998 5C18.1589 5 16.6665 6.49238 16.6665 8.33333V8.90236C12.7825 10.2751 9.99984 13.9793 9.99984 18.3333V23.5974C9.99984 24.4955 9.64308 25.3568 9.00806 25.9918L6.6665 28.3333H14.9998M24.9998 28.3333V30C24.9998 32.7614 22.7613 35 19.9998 35C17.2384 35 14.9998 32.7614 14.9998 30V28.3333M24.9998 28.3333H14.9998" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>

            {/* Сообщения */}
            <button
              className={`nav-icon-btn nav-icon-btn--yellow ${isActive('/messages') ? 'active' : ''}`}
              aria-label="Сообщения"
              onClick={() => handleNavClick('messages', '/messages')}
            >
              <span className="nav-notification-dot">3</span>
              <div className="open-button">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <path d="M30 15.2222C30.0053 17.2754 29.5256 19.3007 28.6 21.1333C27.5024 23.3294 25.8151 25.1765 23.7271 26.4678C21.6391 27.7591 19.2328 28.4435 16.7778 28.4444C14.7246 28.4498 12.6993 27.9701 10.8667 27.0444L2 30L4.95555 21.1333C4.02989 19.3007 3.5502 17.2754 3.55555 15.2222C3.5565 12.7672 4.24095 10.3609 5.53222 8.27289C6.8235 6.18487 8.67061 4.49759 10.8667 3.40004C12.6993 2.47438 14.7246 1.99469 16.7778 2.00004H17.5555C20.7978 2.17892 23.8603 3.54745 26.1564 5.8436C28.4526 8.13974 29.8211 11.2022 30 14.4445V15.2222Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="nav-btn-text">Сообщения</span>
              </div>
            </button>

            {/* Коммиты (Matches) */}
            <button
              className={`nav-icon-btn nav-icon-btn--pink ${isActive('/commits') ? 'active' : ''}`}
              aria-label="Коммиты"
              onClick={() => handleNavClick('commits', '/commits')}
            >
              <div className="open-button">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <path d="M3.25383 5.83802C0.337916 8.64418 0.337916 13.1939 3.25383 16L16.0003 28.2667L28.7466 16C31.6625 13.1939 31.6625 8.64418 28.7466 5.83802C25.8307 3.03186 21.1031 3.03186 18.1872 5.83802L16.0003 7.94272L13.8133 5.83802C10.8974 3.03186 6.16975 3.03186 3.25383 5.83802Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="nav-btn-text">Коммиты</span>
              </div>
            </button>

            {/* Знакомства */}
            <button
              className={`nav-icon-btn nav-icon-btn--yellow ${isActive('/discover') ? 'active' : ''}`}
              aria-label="Знакомства"
              onClick={() => handleNavClick('discover', '/discover')}
            >
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <g clipPath="url(#clip0_nav)">
                  <path d="M13 32.0001C12.7812 32.0001 12.5687 31.9564 12.3687 31.8626C11.9875 31.6939 11.6937 31.3876 11.5437 30.9939L8.89372 24.1063L1.99996 21.4563C1.58746 21.3001 1.26246 20.9688 1.09996 20.5563C0.79371 19.7501 1.19371 18.8438 1.99996 18.5376L8.88747 15.8876L11.5437 9.00008C11.7 8.58757 12.0312 8.26257 12.4437 8.10007C12.8312 7.95007 13.2562 7.96257 13.6375 8.13132C14.0187 8.30007 14.3125 8.60632 14.4625 9.00008L17.1125 15.8876L24 18.5438C24.4125 18.7001 24.7375 19.0313 24.9 19.4438C25.2125 20.2501 24.8062 21.1563 24 21.4626L17.1125 24.1126L14.4562 31.0001C14.3 31.4126 13.9687 31.7376 13.5562 31.9001C13.3812 31.9689 13.1875 32.0001 13 32.0001Z" fill="currentColor" />
                  <path d="M5.50001 11C5.08751 11 4.71251 10.7438 4.56876 10.3563L3.48126 7.51876L0.643751 6.43126C0.25625 6.28751 0 5.91251 0 5.50001C0 5.08751 0.25625 4.71251 0.643751 4.56876L3.48126 3.48126L4.56876 0.643751C4.71251 0.25625 5.08751 0 5.50001 0C5.91251 0 6.28751 0.25625 6.43126 0.643751L7.51876 3.48126L10.3563 4.56876C10.7438 4.71876 11 5.08751 11 5.50001C11 5.91251 10.7438 6.28751 10.3563 6.43126L7.51876 7.51876L6.43126 10.3563C6.28751 10.7438 5.91251 11 5.50001 11Z" fill="currentColor" />
                  <path d="M25 16C24.5875 16 24.2125 15.7438 24.0688 15.3563L22.5625 11.4375L18.6438 9.93126C18.2562 9.78126 18 9.41251 18 9.00001C18 8.58751 18.2562 8.21251 18.6438 8.06876L22.5625 6.56251L24.0688 2.64375C24.2188 2.25625 24.5875 2 25 2C25.4125 2 25.7875 2.25625 25.9313 2.64375L27.4375 6.56251L31.3563 8.06876C31.7438 8.21876 32 8.58751 32 9.00001C32 9.41251 31.7438 9.78751 31.3563 9.93126L27.4375 11.4375L25.9313 15.3563C25.7875 15.7438 25.4125 16 25 16Z" fill="currentColor" />
                </g>
                <defs>
                  <clipPath id="clip0_nav">
                    <rect width="32" height="32" fill="white" />
                  </clipPath>
                </defs>
              </svg>
              <span className="nav-btn-text">Знакомства</span>
            </button>

            {/* Фильтр */}
            <button className="nav-icon-btn nav-icon-btn--yellow" aria-label="Фильтр">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M19.9998 9.99984V6.6665M19.9998 9.99984C18.1589 9.99984 16.6665 11.4922 16.6665 13.3332C16.6665 15.1741 18.1589 16.6665 19.9998 16.6665M19.9998 9.99984C21.8408 9.99984 23.3332 11.4922 23.3332 13.3332C23.3332 15.1741 21.8408 16.6665 19.9998 16.6665M9.99984 29.9998C11.8408 29.9998 13.3332 28.5075 13.3332 26.6665C13.3332 24.8256 11.8408 23.3332 9.99984 23.3332M9.99984 29.9998C8.15889 29.9998 6.6665 28.5075 6.6665 26.6665C6.6665 24.8256 8.15889 23.3332 9.99984 23.3332M9.99984 29.9998V33.3332M9.99984 23.3332V6.6665M19.9998 16.6665V33.3332M29.9998 29.9998C31.8408 29.9998 33.3332 28.5075 33.3332 26.6665C33.3332 24.8256 31.8408 23.3332 29.9998 23.3332M29.9998 29.9998C28.1589 29.9998 26.6665 28.5075 26.6665 26.6665C26.6665 24.8256 28.1589 23.3332 29.9998 23.3332M29.9998 29.9998V33.3332M29.9998 23.3332V6.6665" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </nav>
        </div>

        <div className="header-right">
          <div className="header-user">
            <button className="nav-icon-btn nav-icon-btn--yellow" aria-label="Уведомления">
              <span className="nav-notification-dot">2</span>
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M24.9998 28.3333H33.3332L30.9916 25.9918C30.3566 25.3568 29.9998 24.4955 29.9998 23.5974V18.3333C29.9998 13.9793 27.2171 10.2751 23.3332 8.90236V8.33333C23.3332 6.49238 21.8408 5 19.9998 5C18.1589 5 16.6665 6.49238 16.6665 8.33333V8.90236C12.7825 10.2751 9.99984 13.9793 9.99984 18.3333V23.5974C9.99984 24.4955 9.64308 25.3568 9.00806 25.9918L6.6665 28.3333H14.9998M24.9998 28.3333V30C24.9998 32.7614 22.7613 35 19.9998 35C17.2384 35 14.9998 32.7614 14.9998 30V28.3333M24.9998 28.3333H14.9998" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <div
              className="header-profile-menu-container"
              ref={profileMenuRef}
              style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 'inherit', cursor: 'pointer' }}
              onClick={() => setShowProfileMenu(!showProfileMenu)}
            >
              <img
                src={profile?.avatar_image?.url || '/assets/photos/man_portret (3).png'}
                alt="Аватар"
                className="header-user-avatar"
              />
              <span className="header-user-name">{profile?.username || 'Пользователь'}</span>

              {showProfileMenu && (
                <div className="chat-dropdown-menu" style={{ display: 'flex' }}>
                  <button className="chat-dropdown-item" onClick={(e) => { e.stopPropagation(); navigate('/profile'); setShowProfileMenu(false); }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    Профиль
                  </button>
                  <button
                    className="chat-dropdown-item danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowProfileMenu(false);
                      setShowLogoutModal(true);
                    }}
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                      <polyline points="16 17 21 12 16 7" />
                      <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                    Выйти из профиля
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Logout Modal */}
      {showLogoutModal && (
        <div
          className="modal-overlay"
          style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            backgroundColor: 'rgba(0,0,0,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            animation: 'fadeIn 0.2s ease',
          }}
          onClick={(e) => { if (e.target === e.currentTarget) setShowLogoutModal(false); }}
        >
          <div className="modal-content glass-card-inner animate-scale-in" style={{
            padding: '32px', borderRadius: '16px', textAlign: 'center',
            display: 'flex', flexDirection: 'column', gap: '20px', minWidth: '300px',
          }}>
            <h2 style={{ fontSize: 'var(--fs-24)', color: 'var(--dark-color)', fontWeight: 500 }}>
              Вы точно хотите выйти?
            </h2>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                className="poster-button"
                style={{ backgroundColor: 'var(--supper-accent-color)' }}
                onClick={handleLogout}
              >
                Да
              </button>
              <button
                className="poster-button"
                onClick={() => setShowLogoutModal(false)}
              >
                Нет
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
