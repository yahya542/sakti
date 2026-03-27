import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { useTenantStore } from './store/tenantStore'

// Layouts
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'

// Pages
import Login from './pages/auth/Login'
import Dashboard from './pages/Dashboard'
import Students from './pages/academic/Students'
import Teachers from './pages/academic/Teachers'
import Classes from './pages/academic/Classes'
import Subjects from './pages/academic/Subjects'
import Attendance from './pages/activities/Attendance'
import Scores from './pages/activities/Scores'
import Timeline from './pages/activities/Timeline'
import Invoices from './pages/finance/Invoices'
import Payments from './pages/finance/Payments'
import Settings from './pages/settings/Settings'
import TenantSettings from './pages/settings/TenantSettings'
import RBACSettings from './pages/settings/RBACSettings'
import SmartLinking from './pages/smart_linking/SmartLinking'

// Components
import LoadingSpinner from './components/ui/LoadingSpinner'

function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, user, isLoading } = useAuthStore()
  
  if (isLoading) {
    return <LoadingSpinner />
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />
  }
  
  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
        </Route>
        
        {/* Protected Routes */}
        <Route element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* Academic Routes */}
          <Route path="/academic/students" element={
            <ProtectedRoute roles={['super_admin', 'admin_school', 'teacher']}>
              <Students />
            </ProtectedRoute>
          } />
          <Route path="/academic/teachers" element={
            <ProtectedRoute roles={['super_admin', 'admin_school']}>
              <Teachers />
            </ProtectedRoute>
          } />
          <Route path="/academic/classes" element={
            <ProtectedRoute roles={['super_admin', 'admin_school', 'teacher']}>
              <Classes />
            </ProtectedRoute>
          } />
          <Route path="/academic/subjects" element={
            <ProtectedRoute roles={['super_admin', 'admin_school']}>
              <Subjects />
            </ProtectedRoute>
          } />
          
          {/* Activities Routes */}
          <Route path="/activities/attendance" element={
            <ProtectedRoute roles={['super_admin', 'admin_school', 'teacher']}>
              <Attendance />
            </ProtectedRoute>
          } />
          <Route path="/activities/scores" element={
            <ProtectedRoute roles={['super_admin', 'admin_school', 'teacher']}>
              <Scores />
            </ProtectedRoute>
          } />
          <Route path="/activities/timeline" element={
            <ProtectedRoute roles={['super_admin', 'admin_school', 'teacher', 'parent']}>
              <Timeline />
            </ProtectedRoute>
          } />
          
          {/* Finance Routes */}
          <Route path="/finance/invoices" element={
            <ProtectedRoute roles={['super_admin', 'admin_school', 'parent']}>
              <Invoices />
            </ProtectedRoute>
          } />
          <Route path="/finance/payments" element={
            <ProtectedRoute roles={['super_admin', 'admin_school']}>
              <Payments />
            </ProtectedRoute>
          } />
          
          {/* Smart Linking */}
          <Route path="/smart-linking" element={
            <ProtectedRoute roles={['super_admin', 'admin_school']}>
              <SmartLinking />
            </ProtectedRoute>
          } />
          
          {/* Settings */}
          <Route path="/settings" element={
            <ProtectedRoute roles={['super_admin', 'admin_school']}>
              <Settings />
            </ProtectedRoute>
          } />
          <Route path="/settings/tenant" element={
            <ProtectedRoute roles={['super_admin']}>
              <TenantSettings />
            </ProtectedRoute>
          } />
          <Route path="/settings/rbac" element={
            <ProtectedRoute roles={['super_admin']}>
              <RBACSettings />
            </ProtectedRoute>
          } />
        </Route>
        
        {/* Default Redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App