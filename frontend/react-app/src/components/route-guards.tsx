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
 * PublicRoute — оборачивает маршруты, доступные только неавторизованным.
 * Если пользователь уже авторизован, перенаправляет на /profile.
 */
export const PublicRoute = () => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/profile" replace />;
  }

  return <Outlet />;
};
