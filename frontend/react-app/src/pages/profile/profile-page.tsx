import { useGetMyProfile, useUpdateProfile } from '@/api/hooks';
import { useState } from 'react';

/**
 * ProfilePage — страница профиля текущего пользователя.
 * Показывает фотогалерею, описание, локацию, интересы и т.д.
 */
export const ProfilePage = () => {
  const { data, isLoading, refetch } = useGetMyProfile();
  const updateMutation = useUpdateProfile();
  const profile = data?.profile_data;

  const [editField, setEditField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  const handleSaveField = async (field: string) => {
    try {
      await updateMutation.mutateAsync({ [field]: editValue });
      refetch();
      setEditField(null);
    } catch {
      // Handle error silently
    }
  };

  if (isLoading) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div className="poster-logo animate-scale-in">
          <img src="/assets/icons/Logo.png" className="poster-logo-img" alt="Загрузка" style={{ maxWidth: '120px' }} />
          <p className="poster-logo-text" style={{ fontSize: '1rem' }}>Загрузка...</p>
        </div>
      </section>
    );
  }

  if (!profile) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <p style={{ color: 'var(--dark-color)', fontSize: 'var(--fs-24)' }}>Профиль не найден</p>
      </section>
    );
  }

  const relationshipLabel = (() => {
    switch (profile.relationship_type) {
      case 1: return 'Друга';
      case 2: return 'Партнёра';
      case 3: return 'Нетворкинг';
      default: return 'Не указано';
    }
  })();

  return (
    <section className="commit-page" id="my-profile">
      {/* Left: Photo Gallery Card */}
      <section className="photo-gallery-card glass-card">
        <div className="photo-grid">
          <div className="photo-slot photo-slot--add">
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
              <path d="M40 0V40M40 40V80M40 40H80M40 40H0" stroke="#FF5777" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          {(profile.images || []).map((img) => (
            <div className="photo-slot" key={img.id}>
              <img src={img.url} alt="Фото профиля" />
            </div>
          ))}
          {/* Заполняем пустые слоты если фото мало */}
          {Array.from({ length: Math.max(0, 6 - (profile.images?.length || 0)) }).map((_, i) => (
            <div className="photo-slot photo-slot--add" key={`empty-${i}`} style={{ opacity: 0.3 }}>
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M20 9V33" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M8 21H32" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
          ))}
        </div>
      </section>

      {/* Right: Profile Info Card */}
      <section className="profile-info-card glass-card">
        {/* Header row */}
        <div className="profile-header">
          <div className="profile-avatar">
            <img
              src={profile.avatar_image?.url || '/assets/photos/man_portret (4).png'}
              alt="Аватар"
              className="avatar-img"
            />
          </div>
          <div className="profile-name-group">
            <h1 className="profile-name">{profile.username}, {profile.age}</h1>
            <span className="profile-name-decoration">
              {profile.sign && (
                <>
                  <img src="/assets/main-icons/zodiac-aquarius.png" alt="" />
                  <p className="profile-zodiak-mobile">{profile.sign}</p>
                </>
              )}
            </span>
          </div>
        </div>

        {/* Описание */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels">
            <span className="bio-label">Ваше описание</span>
          </div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content" onClick={() => { setEditField('bio'); setEditValue(profile.bio); }}>
              {editField === 'bio' ? (
                <textarea
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onBlur={() => handleSaveField('bio')}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSaveField('bio')}
                  autoFocus
                  style={{
                    border: 'none', outline: '2px solid var(--main-color)', borderRadius: '8px',
                    padding: '8px', fontFamily: 'inherit', fontSize: 'var(--fs-18)', resize: 'none',
                    minHeight: '60px', width: '100%',
                  }}
                />
              ) : (
                <p className="field-text">{profile.bio || 'Нажмите чтобы добавить описание'}</p>
              )}
            </div>
            <button className="btn-edit field-edit" aria-label="Редактировать" onClick={() => { setEditField('bio'); setEditValue(profile.bio); }}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M13.23 2.232L16.77 5.768M14.73 0.732C15.71 -0.244 17.29 -0.244 18.27 0.732C19.24 1.709 19.24 3.291 18.27 4.268L4.5 18.035H1V14.464L14.73 0.732Z" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>

        {/* Локация */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels">
            <span className="bio-label">Локация</span>
          </div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content">
              <p className="field-text">{profile.city || 'Не указано'}</p>
            </div>
            <button className="btn-edit field-edit" aria-label="Редактировать">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M13.23 2.232L16.77 5.768M14.73 0.732C15.71 -0.244 17.29 -0.244 18.27 0.732C19.24 1.709 19.24 3.291 18.27 4.268L4.5 18.035H1V14.464L14.73 0.732Z" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>

        {/* Вы ищите */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels">
            <span className="bio-label">Вы ищите</span>
          </div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content">
              <p className="field-text">{relationshipLabel}</p>
            </div>
          </div>
        </div>

        {/* Какого человека */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels">
            <span className="bio-label">Какого человека вы ищите?</span>
          </div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content">
              <p className="field-text">{profile.search_for || 'Не указано'}</p>
            </div>
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
            <button className="interest-add-btn" aria-label="Добавить интерес">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 1V8M8 8V15M8 8H15M8 8H1" stroke="#FF5777" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>
      </section>
    </section>
  );
};
