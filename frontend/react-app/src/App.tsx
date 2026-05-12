import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProtectedRoute, PublicRoute } from '@/components/route-guards';
import { MainLayout } from '@/layouts/main-layout';
import { PosterPage } from '@/pages/poster/poster-page';
import { ProfilePage } from '@/pages/profile/profile-page';
import { DiscoverPage } from '@/pages/discover/discover-page';
import { MessagesPage } from '@/pages/messages/messages-page';
import { CommitsPage } from '@/pages/commits/commits-page';
import { UserProfilePage } from '@/pages/user/user-profile-page';

import '@/styles/global.css';

/**
 * QueryClient с настройками по умолчанию:
 * - staleTime: 30 секунд (данные считаются свежими)
 * - retry: 1 попытка перезапроса
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * App — корневой компонент приложения.
 * Настраивает React Query провайдер и маршрутизацию.
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Публичные маршруты (только для неавторизованных) */}
          <Route element={<PublicRoute />}>
            <Route path="/poster" element={<PosterPage />} />
          </Route>

          {/* Защищённые маршруты (требуют авторизации) */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/discover" element={<DiscoverPage />} />
              <Route path="/messages" element={<MessagesPage />} />
              <Route path="/commits" element={<CommitsPage />} />
              <Route path="/user/:userId" element={<UserProfilePage />} />
            </Route>
          </Route>

          {/* Redirect по умолчанию */}
          <Route path="*" element={<Navigate to="/poster" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
