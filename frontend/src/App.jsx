/**
 * App.jsx - Raiz de la aplicacion Wizard404.
 * Router: Login, Home (tarjetas CLI), Scan, Import, Search, Explore, Organize, Cleanup, DocumentDetail.
 * Overlay CRT/VHS opcional: estado en localStorage (wizard404_crt_overlay), toggle con CRTToggleButton.
 */
import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MageProvider } from './context/MageContext'
import { ToastProvider } from './context/ToastContext'
import { ScrollLockProvider } from './context/ScrollLockContext'
import { ToastList } from './components/ToastList'
import { Layout } from './components/Layout'
import { BackgroundImage } from './components/BackgroundImage'
import { ParticleBackground } from './components/ParticleBackground'
import { CRTFilterDefs } from './components/CRTFilterDefs'
import { CRTContentWrapper } from './components/CRTContentWrapper'
import { CRTOverlay } from './components/CRTOverlay'
import { MageWizard } from './components/MageWizard'
import { CRTToggleButton } from './components/CRTToggleButton'
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

const CRT_STORAGE_KEY = 'wizard404_crt_overlay'

function ProtectedRoute({ children }) {
  const { token } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  return children
}

const mainContent = (
  <>
    <BackgroundImage />
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
  </>
)

function App() {
  const [crtOverlayOn, setCrtOverlayOn] = useState(
    () => typeof localStorage !== 'undefined' && localStorage.getItem(CRT_STORAGE_KEY) === 'true'
  )

  const handleCrtToggle = () => {
    setCrtOverlayOn((prev) => {
      const next = !prev
      try {
        localStorage.setItem(CRT_STORAGE_KEY, String(next))
      } catch (_) {}
      return next
    })
  }

  return (
    <BrowserRouter>
      <ScrollLockProvider>
        <MageProvider>
          <ToastProvider>
            <ToastList />
            {crtOverlayOn && <CRTFilterDefs />}
            {crtOverlayOn ? <CRTContentWrapper>{mainContent}</CRTContentWrapper> : mainContent}
            {crtOverlayOn && <CRTOverlay />}
            <CRTToggleButton active={crtOverlayOn} onToggle={handleCrtToggle} />
            <MageWizard crtFilterActive={crtOverlayOn} />
          </ToastProvider>
        </MageProvider>
      </ScrollLockProvider>
    </BrowserRouter>
  )
}

export default App
