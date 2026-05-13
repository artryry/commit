import { useState, useRef, useCallback } from 'react';
import { useGetMatches } from '@/api/hooks';
import { useNavigate } from 'react-router-dom';
import type { ShortProfileSnake } from '@/api/hooks';

const MINIO_PUBLIC_BASE = import.meta.env.VITE_MINIO_URL ?? 'http://localhost:9000';
function profileImageUrl(storageKey: string): string {
  const path = `profile/${storageKey}`.split('/').map(encodeURIComponent).join('/');
  return `${MINIO_PUBLIC_BASE.replace(/\/$/, '')}/${path}`;
}

export const CommitsPage = () => {
  const { data, isLoading } = useGetMatches();
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  const profiles = data?.profiles_data || [];
  const currentProfile = profiles[currentIndex] as ShortProfileSnake | undefined;

  const handleNext = useCallback(() => {
    setCurrentIndex((prev) => prev + 1);
    setCurrentPhotoIndex(0);
  }, []);

  const scrollPhotos = (direction: 'left' | 'right') => {
    if (!currentProfile?.images) return;
    const total = currentProfile.images.length;
    if (direction === 'left') setCurrentPhotoIndex((p) => (p > 0 ? p - 1 : total - 1));
    else setCurrentPhotoIndex((p) => (p < total - 1 ? p + 1 : 0));
  };

  if (isLoading) {
    return (
      <section className="acquaintance-page-container" style={{ display: 'flex' }}>
        <div className="poster-logo animate-scale-in" style={{ margin: 'auto' }}>
          <img src="/assets/icons/Logo.png" className="poster-logo-img" alt="Загрузка" style={{ maxWidth: '100px' }} />
          <p className="poster-logo-text" style={{ fontSize: '0.9rem' }}>Загрузка коммитов...</p>
        </div>
      </section>
    );
  }

  if (!currentProfile || currentIndex >= profiles.length) {
    return (
      <section className="acquaintance-page-container" style={{ display: 'flex' }}>
        <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--dark-color)' }} className="animate-fade-in">
          <svg width="80" height="80" viewBox="0 0 32 32" fill="none" style={{ marginBottom: '20px', opacity: 0.4 }}>
            <path d="M3.25383 5.83802C0.337916 8.64418 0.337916 13.1939 3.25383 16L16.0003 28.2667L28.7466 16C31.6625 13.1939 31.6625 8.64418 28.7466 5.83802C25.8307 3.03186 21.1031 3.03186 18.1872 5.83802L16.0003 7.94272L13.8133 5.83802C10.8974 3.03186 6.16975 3.03186 3.25383 5.83802Z" stroke="var(--supper-accent-color)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <h2 style={{ fontSize: 'var(--fs-32)', marginBottom: '12px' }}>Пока нет коммитов</h2>
          <p style={{ fontSize: 'var(--fs-18)', opacity: 0.6, marginBottom: '24px' }}>Продолжайте знакомиться — взаимные лайки появятся здесь!</p>
          <button className="poster-button" onClick={() => navigate('/discover')}>Начать знакомства</button>
        </div>
      </section>
    );
  }

  const images = currentProfile.images || [];

  return (
    <section className="acquaintance-page-container" style={{ display: 'flex' }}>
      {/* Left: Photo Gallery with horizontal scroll */}
      <section className="photo-gallery-card-x-scroll glass-card">
        <div className="photo-scroll-wrapper">
          <div className="photo-scroll-x">
            {images.length > 0 ? (
              images.map((img, i) => (
                <div className="photo-slot-x" key={img.id} style={{ display: i === currentPhotoIndex ? 'block' : 'none' }}>
                  <img src={profileImageUrl(img.url)} alt={`Фото ${i + 1}`} />
                </div>
              ))
            ) : (
              <div className="photo-slot-x" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--light-color)' }}>
                <p style={{ color: 'var(--dark-color)', opacity: 0.5, fontSize: 'var(--fs-24)' }}>Нет фото</p>
              </div>
            )}
          </div>
          {images.length > 1 && (
            <div className="scroll-buttons">
              <div className="left-btn" onClick={() => scrollPhotos('left')} style={{ cursor: 'pointer' }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6" /></svg>
              </div>
              <div className="right-btn" onClick={() => scrollPhotos('right')} style={{ cursor: 'pointer' }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 6 15 12 9 18" /></svg>
              </div>
            </div>
          )}
        </div>
        {/* Action buttons */}
        <div className="buttons-container">
          <div className="button-like" onClick={() => navigate('/messages')} style={{ cursor: 'pointer' }}>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="22" stroke="#4CAF50" strokeWidth="3" />
              <path d="M14 24L22 32L34 16" stroke="#4CAF50" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div className="button-dislike" onClick={handleNext} style={{ cursor: 'pointer' }}>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="22" stroke="#FF5777" strokeWidth="3" />
              <path d="M16 16L32 32M32 16L16 32" stroke="#FF5777" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        </div>
      </section>

      {/* Right: Profile Info Card */}
      <section className="another-profile-info-card glass-card">
        <div className="scroll-container">
          <div className="profile-main-info">
            <div className="profile-name-group">
              <h1 className="profile-name">{currentProfile.username}, {currentProfile.age}</h1>
            </div>
            <div className="sec-line">
              <h2 className="city">{currentProfile.city || 'Не указано'}</h2>
              {currentProfile.sign && (
                <div className="zodiak"><span style={{ fontSize: 'var(--fs-18)', color: 'var(--dark-color)' }}>{currentProfile.sign}</span></div>
              )}
            </div>
            <div className="description"><p>{currentProfile.bio || 'Нет описания'}</p></div>
          </div>
          <div className="profile-item-frame">
            <div className="profile-bio-labels"><span className="bio-label">Интересы</span></div>
            <div className="interests-container">
              {(currentProfile.tags || []).map((tag, i) => (
                <span className="interest-tag" key={i}>#{tag}</span>
              ))}
            </div>
          </div>
        </div>
      </section>
    </section>
  );
};
