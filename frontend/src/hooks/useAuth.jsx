/**
 * hooks/useAuth.jsx - Estado de autenticación.
 * Token en localStorage para persistir sesión.
 */
import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('wizard404_token'))
  const [user, setUser] = useState(() => {
    const u = localStorage.getItem('wizard404_user')
    return u ? JSON.parse(u) : null
  })

  const login = (data) => {
    setToken(data.access_token)
    setUser({ id: data.user_id, name: data.user_name })
    localStorage.setItem('wizard404_token', data.access_token)
    localStorage.setItem('wizard404_user', JSON.stringify({ id: data.user_id, name: data.user_name }))
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('wizard404_token')
    localStorage.removeItem('wizard404_user')
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

/* eslint-disable react-refresh/only-export-components -- useAuth y AuthProvider se usan juntos */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
