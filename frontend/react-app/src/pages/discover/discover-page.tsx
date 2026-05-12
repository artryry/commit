import { useState, useRef, useCallback } from 'react';
import { useGetRecommendations, useSwipeAction, useGetCompatibility } from '@/api/hooks';
import type { ShortProfileProtoJson } from '@/api/hooks';

/**
 * DiscoverPage — страница знакомств (аналог Acquaintance).
 * Показывает карточки рекомендованных пользователей со свайпами.
 */
export const DiscoverPage = () => {
  const { data, isLoading, refetch } = useGetRecommendations();
  const swipeMutation = useSwipeAction();
  const compatibilityMutation = useGetCompatibility();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [compatibilityText, setCompatibilityText] = useState<string | null>(null);
  const [showAstrology, setShowAstrology] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const profiles = data?.profilesData || [];
  const currentProfile = profiles[currentIndex] as ShortProfileProtoJson | undefined;

  const handleSwipe = useCallback(async (liked: boolean) => {
    if (!currentProfile) return;
    try {
      await swipeMutation.mutateAsync({
        target_user_id: Number(currentProfile.userId),
        liked,
      });
    } catch {
      // Ignore swipe errors
    }
    setCurrentIndex((prev) => prev + 1);
    setCurrentPhotoIndex(0);
    setCompatibilityText(null);
    setShowAstrology(false);
  }, [currentProfile, swipeMutation]);

  const handleLoadCompatibility = useCallback(async () => {
    if (!currentProfile) return;
    try {
      const res = await compatibilityMutation.mutateAsync({
        user_ids: [Number(currentProfile.userId)],
      });
      const item = res.items?.[0];
      setCompatibilityText(item?.text || 'Совместимость не определена');
      setShowAstrology(true);
    } catch {
      setCompatibilityText('Не удалось загрузить совместимость');
      setShowAstrology(true);
    }
  }, [currentProfile, compatibilityMutation]);

  const scrollPhotos = (direction: 'left' | 'right') => {
    if (!currentProfile?.images) return;
    const total = currentProfile.images.length;
    if (direction === 'left') {
      setCurrentPhotoIndex((prev) => (prev > 0 ? prev - 1 : total - 1));
    } else {
      setCurrentPhotoIndex((prev) => (prev < total - 1 ? prev + 1 : 0));
    }
  };

  if (isLoading) {
    return (
      <section className="acquaintance-page-container" style={{ display: 'flex' }}>
        <div className="poster-logo animate-scale-in" style={{ margin: 'auto' }}>
          <img src="/assets/icons/Logo.png" className="poster-logo-img" alt="Загрузка" style={{ maxWidth: '100px' }} />
          <p className="poster-logo-text" style={{ fontSize: '0.9rem' }}>Ищем людей...</p>
        </div>
      </section>
    );
  }

  if (!currentProfile || currentIndex >= profiles.length) {
    return (
      <section className="acquaintance-page-container" style={{ display: 'flex' }}>
        <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--dark-color)' }} className="animate-fade-in">
          <h2 style={{ fontSize: 'var(--fs-32)', marginBottom: '16px' }}>Пока нет новых профилей</h2>
          <p style={{ fontSize: 'var(--fs-18)', opacity: 0.6, marginBottom: '24px' }}>Мы уже ищем новых людей для вас!</p>
          <button
            className="poster-button"
            onClick={() => { setCurrentIndex(0); refetch(); }}
          >
            Обновить
          </button>
        </div>
      </section>
    );
  }

  const images = currentProfile.images || [];
  const displayImage = images[currentPhotoIndex]?.url;

  return (
    <section className="acquaintance-page-container" style={{ display: 'flex' }}>
      {/* Left: Photo Gallery with horizontal scroll */}
      <section className="photo-gallery-card-x-scroll glass-card">
        <div className="photo-scroll-wrapper">
          <div className="photo-scroll-x" ref={scrollRef}>
            {images.length > 0 ? (
              images.map((img, i) => (
                <div
                  className="photo-slot-x"
                  key={img.id}
                  style={{ display: i === currentPhotoIndex ? 'block' : 'none' }}
                >
                  <img src={img.url} alt={`Фото ${i + 1}`} />
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
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
              </div>
              <div className="right-btn" onClick={() => scrollPhotos('right')} style={{ cursor: 'pointer' }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--dark-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 6 15 12 9 18" />
                </svg>
              </div>
            </div>
          )}
        </div>

        {/* Like / Dislike buttons */}
        <div className="buttons-container">
          <div
            className="button-like"
            onClick={() => handleSwipe(true)}
            style={{ cursor: 'pointer' }}
          >
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="22" stroke="#4CAF50" strokeWidth="3" />
              <path d="M14 24L22 32L34 16" stroke="#4CAF50" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div
            className="button-dislike"
            onClick={() => handleSwipe(false)}
            style={{ cursor: 'pointer' }}
          >
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
              <h1 className="profile-name">
                {currentProfile.username}, {currentProfile.age}
              </h1>
            </div>
            <div className="sec-line">
              <h2 className="city">{currentProfile.city || 'Не указано'}</h2>
              {currentProfile.sign && (
                <div className="zodiak">
                  <span style={{ fontSize: 'var(--fs-18)', color: 'var(--dark-color)' }}>
                    {currentProfile.sign}
                  </span>
                </div>
              )}
            </div>
            <div className="description">
              <p>{currentProfile.bio || 'Нет описания'}</p>
            </div>
          </div>

          {/* Интересы */}
          <div className="profile-item-frame">
            <div className="profile-bio-labels">
              <span className="bio-label">Интересы</span>
            </div>
            <div className="interests-container">
              {(currentProfile.tags || []).map((tag, i) => (
                <span className="interest-tag" key={i}>#{tag}</span>
              ))}
            </div>
          </div>

          {/* Астрология */}
          <details className="astrology-container-commit" open={showAstrology}>
            <summary
              className="text-field-astrology"
              onClick={(e) => {
                if (!compatibilityText) {
                  e.preventDefault();
                  handleLoadCompatibility();
                }
              }}
            >
              Натальная карта
              <svg width="14" height="8" viewBox="0 0 14 8" fill="none" style={{ marginLeft: '8px' }}>
                <path d="M1 1L7 7L13 1" stroke="var(--dark-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </summary>
            <div className="astrology-content-wrapper">
              <div className="general-match">
                <h3>Общая совместимость</h3>
                <p className="astrology-description">
                  {compatibilityMutation.isPending
                    ? 'Загрузка совместимости...'
                    : compatibilityText || 'Нажмите, чтобы узнать совместимость'
                  }
                </p>
              </div>
            </div>
          </details>
        </div>
      </section>
    </section>
  );
};
