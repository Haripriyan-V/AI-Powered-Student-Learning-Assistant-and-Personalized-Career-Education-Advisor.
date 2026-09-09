import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { ThemeProvider } from './context/ThemeContext';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <ThemeProvider>
      <AppRoutes />
      <ToastContainer
        position="top-right"
        autoClose={3500}
        newestOnTop
        theme="colored"
        toastClassName="!rounded-xl !text-sm"
      />
    </ThemeProvider>
  );
}

export default App;
