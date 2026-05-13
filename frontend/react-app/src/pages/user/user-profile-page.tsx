import { useParams } from 'react-router-dom';
import { useGetProfileById, useGetCompatibility } from '@/api/hooks';
import { useState, useCallback } from 'react';
import { ZodiacIcon } from '@/components/zodiac-icon';

const MINIO_PUBLIC_BASE = import.meta.env.VITE_MINIO_URL ?? 'http://localhost:9000';
function profileImageUrl(storageKey: string): string {
  const path = `profile/${storageKey}`.split('/').map(encodeURIComponent).join('/');
  return `${MINIO_PUBLIC_BASE.replace(/\/$/, '')}/${path}`;
}

/**
 * UserProfilePage — страница просмотра профиля другого пользователя.
 */
export const UserProfilePage = () => {
  const { userId } = useParams<{ userId: string }>();
  const numericId = Number(userId);
  const { data, isLoading } = useGetProfileById(numericId);
  const compatibilityMutation = useGetCompatibility();

  const [compatibilityText, setCompatibilityText] = useState<string | null>(null);
  const [showAstrology, setShowAstrology] = useState(false);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  const profile = data?.profile_data;

  const handleLoadCompatibility = useCallback(async () => {
    if (!numericId) return;
    try {
      const res = await compatibilityMutation.mutateAsync({
        user_ids: [numericId],
      });
      const item = res.items?.[0];
      setCompatibilityText(item?.text || 'Совместимость не определена');
      setShowAstrology(true);
    } catch {
      setCompatibilityText('Не удалось загрузить совместимость');
      setShowAstrology(true);
    }
  }, [numericId, compatibilityMutation]);

  if (isLoading) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center' }}>
        <div className="poster-logo animate-scale-in" style={{ margin: 'auto' }}>
          <img src="/assets/icons/Logo.png" className="poster-logo-img" alt="Загрузка" style={{ maxWidth: '100px' }} />
          <p className="poster-logo-text" style={{ fontSize: '0.9rem' }}>Загрузка...</p>
        </div>
      </section>
    );
  }

  if (!profile) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center' }}>
        <p style={{ color: 'var(--dark-color)', fontSize: 'var(--fs-24)' }}>Профиль не найден</p>
      </section>
    );
  }

  const images = profile.images || [];

  return (
    <section className="another-user-page-container" style={{ display: 'flex' }}>
      {/* Left: Photo Gallery */}
      <section className="photo-gallery-card glass-card">
        <div className="photo-grid">
          {images.length > 0 ? (
            images.map((img) => (
              <div className="photo-slot" key={img.id}>
                <img src={profileImageUrl(img.url)} alt="Фото" />
              </div>
            ))
          ) : (
            <div className="photo-slot" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--light-color)', gridColumn: '1 / -1', minHeight: '200px' }}>
              <p style={{ color: 'var(--dark-color)', opacity: 0.5 }}>Нет фото</p>
            </div>
          )}
        </div>
      </section>

      {/* Right: Profile Info */}
      <section className="another-profile-info-card glass-card">
        <div className="scroll-container">
          <div className="profile-main-info">
            <div className="profile-name-group">
              <h1 className="profile-name">{profile.username}, {profile.age}</h1>
            </div>
            <div className="sec-line">
              <h2 className="city">{profile.city || 'Не указано'}</h2>
              {profile.sign && (
                <div className="zodiak">
                  <ZodiacIcon sign={profile.sign} style={{ color: 'var(--dark-color)' }} />
                </div>
              )}
            </div>
            <div className="description">
              <p>{profile.bio || 'Нет описания'}</p>
            </div>
          </div>

          {/* Интересы */}
          <div className="profile-item-frame">
            <div className="profile-bio-labels">
              <span className="bio-label">Интересы</span>
            </div>
            <div className="interests-container">
              {(profile.tags || []).map((tag, i) => (
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
