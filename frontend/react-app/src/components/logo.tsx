/**
 * Logo — компонент логотипа Commit (иконка + текст).
 * Используется на Poster и в Header.
 */
export const Logo = ({ size = 'large' }: { size?: 'large' | 'small' }) => (
  <div className="poster-logo">
    <img
      src="/assets/icons/Logo.png"
      className="poster-logo-img"
      alt="Логотип Commit"
      style={size === 'small' ? { maxWidth: '120px', maxHeight: '80px' } : undefined}
    />
    <p className="poster-logo-text">COMMIT</p>
  </div>
);
