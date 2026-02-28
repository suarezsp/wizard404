/**
 * Login.jsx - Pantalla de login.
 * Nombre + contraseña. Estilo 16-bit.
 * Comprueba health del backend al montar; muestra aviso si no esta disponible.
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { useToast } from '../context/ToastContext'
import { friendlyMessage } from '../utils/toastMessages'
import { login, register, healthCheck } from '../api/client'
import { Card } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'

export function Login() {
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [backendOk, setBackendOk] = useState(true)
  const { login: doLogin } = useAuth()
  const { sayForScene } = useMage()
  const { addToast } = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    sayForScene('login')
  }, [sayForScene])

  useEffect(() => {
    if (isRegister) sayForScene('register')
  }, [isRegister, sayForScene])

  useEffect(() => {
    let cancelled = false
    healthCheck().then((res) => {
      if (!cancelled) setBackendOk(res && !res.error)
    })
    return () => { cancelled = true }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = isRegister ? await register(name, password) : await login(name, password)
      doLogin(data)
      navigate('/')
    } catch (err) {
      addToast(friendlyMessage(err.message) || 'Error al iniciar sesion', 'error')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card variant="light" borderWidth={4} className="p-8 max-w-md w-full">
        <h1 className="text-[var(--pixel-accent)] text-center text-xl mb-6 font-pixel">
          WIZARD404
        </h1>
        <p className="text-[var(--pixel-muted)] text-center text-xs mb-6">
          Document Search & Management
        </p>
        {!backendOk && (
          <p className="text-amber-400 text-xs text-center mb-4">
            Backend no disponible. Comprueba que el servidor este en marcha.
          </p>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            variant="light"
            label="Nombre"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input
            variant="light"
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" className="w-full py-3">
            {isRegister ? 'REGISTRAR' : 'ENTRAR'}
          </Button>
        </form>
        <Button type="button" variant="ghost" className="mt-4 w-full" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? 'Ya tengo cuenta' : 'Crear cuenta'}
        </Button>
      </Card>
    </div>
  )
}
