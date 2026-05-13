import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';

/**
 * ProtectedRoute — оборачивает маршруты, требующие аутентификации.
 * Если пользователь не авторизован, перенаправляет на /poster.
 */
export const ProtectedRoute = () => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/poster" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

/**
 * PublicRoute — оборачивает маршруты, доступные только неавторизованным
 * ИЛИ авторизованным без профиля (онбординг).
 *
 * Редирект на /discover происходит ТОЛЬКО когда пользователь
 * авторизован И профиль уже заполнен (hasProfile === true).
 */
export const PublicRoute = () => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hasProfile = useAuthStore((s) => s.hasProfile);

  // Авторизован + профиль заполнен → уходим на main
  if (isAuthenticated && hasProfile) {
    return <Navigate to="/discover" replace />;
  }

  // Либо не авторизован, либо авторизован но без профиля (онбординг) → остаёмся
  return <Outlet />;
};
