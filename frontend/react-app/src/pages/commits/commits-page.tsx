import { useGetMatches } from '@/api/hooks';
import { useNavigate } from 'react-router-dom';
import type { ShortProfileSnake } from '@/api/hooks';

/**
 * CommitsPage — страница «Коммиты» (матчи).
 * Показывает карточки пользователей, с которыми произошёл взаимный лайк.
 */
export const CommitsPage = () => {
  const { data, isLoading } = useGetMatches();
  const navigate = useNavigate();

  const profiles = data?.profiles_data || [];

  if (isLoading) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center' }}>
        <div className="poster-logo animate-scale-in" style={{ margin: 'auto' }}>
          <img src="/assets/icons/Logo.png" className="poster-logo-img" alt="Загрузка" style={{ maxWidth: '100px' }} />
          <p className="poster-logo-text" style={{ fontSize: '0.9rem' }}>Загрузка коммитов...</p>
        </div>
      </section>
    );
  }

  if (profiles.length === 0) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: 'var(--dark-color)' }} className="animate-fade-in">
          <svg width="80" height="80" viewBox="0 0 32 32" fill="none" style={{ marginBottom: '20px', opacity: 0.4 }}>
            <path d="M3.25383 5.83802C0.337916 8.64418 0.337916 13.1939 3.25383 16L16.0003 28.2667L28.7466 16C31.6625 13.1939 31.6625 8.64418 28.7466 5.83802C25.8307 3.03186 21.1031 3.03186 18.1872 5.83802L16.0003 7.94272L13.8133 5.83802C10.8974 3.03186 6.16975 3.03186 3.25383 5.83802Z" stroke="var(--supper-accent-color)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <h2 style={{ fontSize: 'var(--fs-32)', marginBottom: '12px' }}>Пока нет коммитов</h2>
          <p style={{ fontSize: 'var(--fs-18)', opacity: 0.6, marginBottom: '24px' }}>
            Продолжайте знакомиться — взаимные лайки появятся здесь!
          </p>
          <button className="poster-button" onClick={() => navigate('/discover')}>
            Начать знакомства
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="commit-page" style={{ flexWrap: 'wrap', alignItems: 'flex-start', overflowY: 'auto', padding: '20px', gap: '16px' }}>
      {profiles.map((profile) => (
        <MatchCard
          key={profile.user_id}
          profile={profile}
          onClick={() => navigate(`/user/${profile.user_id}`)}
          onMessage={() => navigate('/messages')}
        />
      ))}
    </section>
  );
};

/** Карточка матча */
const MatchCard = ({
  profile,
  onClick,
  onMessage,
}: {
  profile: ShortProfileSnake;
  onClick: () => void;
  onMessage: () => void;
}) => {
  return (
    <div
      className="glass-card animate-fade-in"
      style={{
        width: 'clamp(260px, 30vw, 380px)',
        padding: 'clamp(12px, 1vw, 20px)',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        cursor: 'pointer',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
      }}
      onClick={onClick}
      onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-4px)'; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'; }}
    >
      {/* Avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <img
          src={profile.avatar_image?.url || '/assets/photos/man_portret (2).png'}
          alt={profile.username}
          style={{
            width: 'clamp(48px, 4vw, 72px)',
            height: 'clamp(48px, 4vw, 72px)',
            borderRadius: '12px',
            objectFit: 'cover',
          }}
        />
        <div>
          <h3 style={{ fontSize: 'var(--fs-24)', color: 'var(--dark-color)', fontWeight: 500 }}>
            {profile.username}, {profile.age}
          </h3>
          <p style={{ fontSize: 'var(--fs-12)', color: 'var(--dark-color)', opacity: 0.6 }}>
            {profile.city || ''}
            {profile.sign ? ` • ${profile.sign}` : ''}
          </p>
        </div>
      </div>

      {/* Bio */}
      {profile.bio && (
        <p style={{
          fontSize: 'var(--fs-18)',
          color: 'var(--dark-color)',
          lineHeight: 1.4,
          opacity: 0.8,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
        }}>
          {profile.bio}
        </p>
      )}

      {/* Tags */}
      {profile.tags && profile.tags.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {profile.tags.slice(0, 4).map((tag, i) => (
            <span className="interest-tag" key={i} style={{ fontSize: 'var(--fs-12)', padding: '4px 10px' }}>
              #{tag}
            </span>
          ))}
          {profile.tags.length > 4 && (
            <span style={{ fontSize: 'var(--fs-12)', color: 'var(--dark-color)', opacity: 0.5, alignSelf: 'center' }}>
              +{profile.tags.length - 4}
            </span>
          )}
        </div>
      )}

      {/* Action button */}
      <button
        className="poster-button"
        style={{ fontSize: 'var(--fs-18)', padding: '8px 20px', alignSelf: 'center' }}
        onClick={(e) => { e.stopPropagation(); onMessage(); }}
      >
        Написать
      </button>
    </div>
  );
};
