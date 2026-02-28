/**
 * ToastContext.jsx - Notificaciones emergentes (errores, avisos) en la parte superior.
 * Estetica 16-bit; auto-cierre y cierre manual.
 */
import { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

const TOAST_AUTO_CLOSE_MS = 5000

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'error') => {
    const id = Math.random().toString(36).slice(2)
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, TOAST_AUTO_CLOSE_MS)
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const value = { toasts, addToast, removeToast }
  return (
    <ToastContext.Provider value={value}>
      {children}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
