import './progress-indicator.css';

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

/**
 * Красивый индикатор прогресса для многошагового онбординга.
 * Отображает активный шаг, завершённые и оставшиеся.
 */
export const ProgressIndicator = ({ currentStep, totalSteps }: ProgressIndicatorProps) => {
  return (
    <div className="progress-indicator">
      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${((currentStep) / totalSteps) * 100}%` }}
        />
      </div>
      <div className="progress-dots">
        {Array.from({ length: totalSteps }, (_, i) => (
          <div
            key={i}
            className={`progress-dot ${
              i < currentStep ? 'completed' : i === currentStep ? 'active' : ''
            }`}
          >
            {i < currentStep && (
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </div>
        ))}
      </div>
      <span className="progress-label">
        Шаг {currentStep + 1} из {totalSteps}
      </span>
    </div>
  );
};
