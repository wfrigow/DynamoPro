import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectAuth } from './store/slices/authSlice';

// Layouts
import MainLayout from './layouts/MainLayout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import TestPage from './pages/TestPage';
import Profile from './pages/Profile';
import Energy from './pages/Energy';
import Water from './pages/Water';
import Recommendations from './pages/Recommendations';
import SubsidiesPage from './pages/SubsidiesPage';
import SubsidyDetailsPage from './pages/SubsidyDetailsPage';
import SubsidyApplicationPage from './pages/SubsidyApplicationPage';
import SubsidyTrackingPage from './pages/SubsidyTrackingPage';
import Suppliers from './pages/Suppliers';
import Projects from './pages/Projects';
import GreenPassport from './pages/GreenPassport';
import AuditPage from './pages/AuditPage';
import NotFound from './pages/NotFound';

// Components
import TestComponent from './components/TestComponent';

const App: React.FC = () => {
  const { isAuthenticated } = useSelector(selectAuth);
  
  // Protected route component
  const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
  };

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/test" element={<TestPage />} />
      
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<TestComponent />} />
        <Route path="profile" element={<Profile />} />
        <Route path="energy" element={<Energy />} />
        <Route path="water" element={<Water />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="subsidies" element={<SubsidiesPage />} />
        <Route path="subsidies/details/:subsidyId" element={<SubsidyDetailsPage />} />
        <Route path="subsidies/apply/:subsidyId" element={<SubsidyApplicationPage />} />
        <Route path="subsidies/track/:applicationId" element={<SubsidyTrackingPage />} />
        <Route path="suppliers" element={<Suppliers />} />
        <Route path="projects" element={<Projects />} />
        <Route path="green-passport" element={<GreenPassport />} />
        <Route path="audit" element={<AuditPage />} />
      </Route>
      
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default App;
