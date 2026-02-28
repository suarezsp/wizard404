/**
 * ScrollLockContext - Controla si la pagina puede hacer scroll (y con ello el parallax).
 * Scroll permitido solo en /scan, /import, /search y /explore; el resto tiene scroll bloqueado.
 */
import { createContext, useContext, useEffect, useMemo } from 'react'
import { useLocation } from 'react-router-dom'

const ScrollLockContext = createContext(null)

const SCROLL_ROUTES = ['/scan', '/import', '/search', '/explore']

function isScrollRoute(pathname) {
  return SCROLL_ROUTES.includes(pathname)
}

export function ScrollLockProvider({ children }) {
  const { pathname } = useLocation()
  const scrollEnabled = useMemo(() => isScrollRoute(pathname), [pathname])

  useEffect(() => {
    const el = document.body
    const prev = el.style.overflow
    el.style.overflow = scrollEnabled ? 'auto' : 'hidden'
    return () => {
      el.style.overflow = prev
    }
  }, [scrollEnabled])

  const value = useMemo(() => ({ scrollEnabled }), [scrollEnabled])

  return (
    <ScrollLockContext.Provider value={value}>
      {children}
    </ScrollLockContext.Provider>
  )
}

export function useScrollLock() {
  const ctx = useContext(ScrollLockContext)
  if (!ctx) throw new Error('useScrollLock must be used within ScrollLockProvider')
  return ctx
}
