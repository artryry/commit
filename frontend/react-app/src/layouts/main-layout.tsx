import { Outlet } from 'react-router-dom';
import { SiteHeader } from '@/components/header';
import { BackgroundElements } from '@/components/background-elements';
import '@/styles/main.css';

/**
 * MainLayout — обёртка для авторизованных страниц.
 * Header + фоновые элементы + контент через Outlet.
 */
export const MainLayout = () => {
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
