/**
 * App.jsx - Raiz de la aplicacion Wizard404.
 * Router: Login, Home (tarjetas CLI), Scan, Import, Search, Explore, Organize, Cleanup, DocumentDetail.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MageProvider } from './context/MageContext'
import { ToastProvider } from './context/ToastContext'
import { ToastList } from './components/ToastList'
import { Layout } from './components/Layout'
import { ParticleBackground } from './components/ParticleBackground'
import { RouteTransition } from './components/RouteTransition'
import { Login } from './pages/Login'
import { Home } from './pages/Home'
import { Scan } from './pages/Scan'
import { Import } from './pages/Import'
import { Search } from './pages/Search'
import { Explore } from './pages/Explore'
import { Organize } from './pages/Organize'
import { Cleanup } from './pages/Cleanup'
import { DocumentDetail } from './pages/DocumentDetail'
import { useAuth } from './hooks/useAuth'

function ProtectedRoute({ children }) {
  const { token } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  return children
}

function App() {
  return (
    <BrowserRouter>
      <MageProvider>
        <ToastProvider>
          <ToastList />
          <ParticleBackground />
          <Layout>
          <RouteTransition>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
              <Route path="/scan" element={<ProtectedRoute><Scan /></ProtectedRoute>} />
              <Route path="/import" element={<ProtectedRoute><Import /></ProtectedRoute>} />
              <Route path="/search" element={<ProtectedRoute><Search /></ProtectedRoute>} />
              <Route path="/explore" element={<ProtectedRoute><Explore /></ProtectedRoute>} />
              <Route path="/organize" element={<ProtectedRoute><Organize /></ProtectedRoute>} />
              <Route path="/cleanup" element={<ProtectedRoute><Cleanup /></ProtectedRoute>} />
              <Route path="/documents/:id" element={<ProtectedRoute><DocumentDetail /></ProtectedRoute>} />
            </Routes>
          </RouteTransition>
        </Layout>
        </ToastProvider>
      </MageProvider>
    </BrowserRouter>
  )
}

export default App
