import { Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useRoutes } from 'react-router-dom';
import routes from '~react-pages';

export function Router() {
  return (
    <BrowserRouter>
      <Suspense fallback={<p>Loading...</p>}>
        <Routes>
          {useRoutes(routes)}
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}