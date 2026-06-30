import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ApplicationForm from './pages/ApplicationForm';
import ApplicationStatus from './pages/ApplicationStatus';
import AdminDashboard from './pages/AdminDashboard';
import { Toaster } from '@/components/ui/sonner';

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={user ? <Navigate to="/apply" replace /> : <LoginPage />} />
      <Route path="/register" element={user ? <Navigate to="/apply" replace /> : <RegisterPage />} />
      <Route
        path="/apply"
        element={
          <ProtectedRoute>
            <ApplicationForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/status/:threadId"
        element={
          <ProtectedRoute>
            <ApplicationStatus />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <div className="grain-texture" />
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
