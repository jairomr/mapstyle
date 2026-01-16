import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Creator } from './pages/Creator';
import { Viewer } from './pages/Viewer';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Creator />} />
          <Route path="/:urlKey" element={<Viewer />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
