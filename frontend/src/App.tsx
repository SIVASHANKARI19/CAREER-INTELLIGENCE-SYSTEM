import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardShell } from './components/layout/DashboardShell';

// Auth Pages
import { Login } from './pages/auth/Login';
import { Register } from './pages/auth/Register';
import { ForgotPassword } from './pages/auth/ForgotPassword';

// Student Pages
import { Dashboard } from './pages/student/Dashboard';
import { Profile } from './pages/student/Profile';
import { Resume } from './pages/student/Resume';
import { GitHubPage } from './pages/student/GitHub';
import { LinkedInPage } from './pages/student/LinkedIn';
import { FusionPage } from './pages/student/Fusion';
import { ReadinessPage } from './pages/student/Readiness';
import { SkillGapPage } from './pages/student/SkillGap';
import { RoadmapPage } from './pages/student/Roadmap';
import { SimulatorPage } from './pages/student/Simulator';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { StudentManagement } from './pages/admin/StudentManagement';
import { DatasetManagement } from './pages/admin/DatasetManagement';
import { ModelRetraining } from './pages/admin/ModelRetraining';
import { CompanyRequirements } from './pages/admin/CompanyRequirements';
import { Analytics } from './pages/admin/Analytics';

const ProtectedRoute: React.FC<{ children: React.ReactNode; requireAdmin?: boolean }> = ({
  children,
  requireAdmin = false,
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F3F2EF] dark:bg-[#1D2226]">
        <div className="flex items-center gap-3 text-linkedin-blue">
          <div className="w-8 h-8 rounded-full border-2 border-linkedin-blue border-t-transparent animate-spin" />
          <span className="text-sm font-semibold">Loading PlacementAI...</span>
        </div>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;
  if (requireAdmin && user.role !== 'admin') return <Navigate to="/dashboard" replace />;

  return <>{children}</>;
};

const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      {/* Protected student routes */}
      <Route path="/dashboard" element={<ProtectedRoute><DashboardShell><Dashboard /></DashboardShell></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><DashboardShell><Profile /></DashboardShell></ProtectedRoute>} />
      <Route path="/resume" element={<ProtectedRoute><DashboardShell><Resume /></DashboardShell></ProtectedRoute>} />
      <Route path="/github" element={<ProtectedRoute><DashboardShell><GitHubPage /></DashboardShell></ProtectedRoute>} />
      <Route path="/linkedin" element={<ProtectedRoute><DashboardShell><LinkedInPage /></DashboardShell></ProtectedRoute>} />
      <Route path="/fusion" element={<ProtectedRoute><DashboardShell><FusionPage /></DashboardShell></ProtectedRoute>} />
      <Route path="/readiness" element={<ProtectedRoute><DashboardShell><ReadinessPage /></DashboardShell></ProtectedRoute>} />
      <Route path="/skill-gap" element={<ProtectedRoute><DashboardShell><SkillGapPage /></DashboardShell></ProtectedRoute>} />
      <Route path="/roadmap" element={<ProtectedRoute><DashboardShell><RoadmapPage /></DashboardShell></ProtectedRoute>} />
      <Route path="/simulator" element={<ProtectedRoute><DashboardShell><SimulatorPage /></DashboardShell></ProtectedRoute>} />

      {/* Protected admin routes */}
      <Route path="/admin" element={<ProtectedRoute requireAdmin><DashboardShell><AdminDashboard /></DashboardShell></ProtectedRoute>} />
      <Route path="/admin/students" element={<ProtectedRoute requireAdmin><DashboardShell><StudentManagement /></DashboardShell></ProtectedRoute>} />
      <Route path="/admin/dataset" element={<ProtectedRoute requireAdmin><DashboardShell><DatasetManagement /></DashboardShell></ProtectedRoute>} />
      <Route path="/admin/model-retrain" element={<ProtectedRoute requireAdmin><DashboardShell><ModelRetraining /></DashboardShell></ProtectedRoute>} />
      <Route path="/admin/company-requirements" element={<ProtectedRoute requireAdmin><DashboardShell><CompanyRequirements /></DashboardShell></ProtectedRoute>} />
      <Route path="/admin/analytics" element={<ProtectedRoute requireAdmin><DashboardShell><Analytics /></DashboardShell></ProtectedRoute>} />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

export default App;
