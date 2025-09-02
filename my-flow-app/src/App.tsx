import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { type ReactNode } from 'react'
import './App.css'

// Pages / Components
import LoginPage from '../src/LoginPage'
import SignupPage from '../src/SignupPage'
import Dashboard from '../src/contexts/Dashboard'
import WorkflowEditor from '../src/contexts/WorkFlow'
import { AuthProvider, useAuth } from './contexts/AuthContext'

// Protected Route Component
interface ProtectedRouteProps {
  children: ReactNode;
}
function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

// AppContent avec toutes les routes
function AppContent() {
  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Auth routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/workflow" 
          element={
            <ProtectedRoute>
              <WorkflowEditor />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/workflow/new" 
          element={
            <ProtectedRoute>
              <WorkflowEditor />
            </ProtectedRoute>
          } 
        />

        {/* Redirect root */}
        <Route path="/" element={<Navigate to="/dashboard" />} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </div>
  )
}

// App avec AuthProvider et Router
function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  )
}

export default App
