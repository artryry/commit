import { Outlet } from 'react-router-dom';
import { SiteHeader } from '@/components/header';
import { BackgroundElements } from '@/components/background-elements';
import { useNotificationsWs } from '@/hooks/use-notifications-ws';
import '@/styles/main.css';

/**
 * MainLayout — обёртка для авторизованных страниц.
 * Header + фоновые элементы + контент через Outlet.
 * Подключает WebSocket уведомлений для всех авторизованных страниц.
 */
export const MainLayout = () => {
  useNotificationsWs();

  return (
    <>
      <SiteHeader />
      <BackgroundElements />
      <main className="profile-layout">
        <Outlet />
      </main>
    </>
  );
};
