/**
 * Login.test.jsx - Tests de la página Login (formulario, envío, error).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Login } from './Login'

const mockDoLogin = vi.fn()
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ login: mockDoLogin }),
}))
vi.mock('../context/MageContext', () => ({
  useMage: () => ({ sayForScene: vi.fn() }),
}))
vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ addToast: vi.fn() }),
}))

const mockLogin = vi.fn()
const mockRegister = vi.fn()
const mockHealthCheck = vi.fn()
vi.mock('../api/client', () => ({
  login: (...args) => mockLogin(...args),
  register: (...args) => mockRegister(...args),
  healthCheck: () => mockHealthCheck(),
}))

describe('Login', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockHealthCheck.mockResolvedValue({ status: 'ok' })
  })

  it('renderiza formulario con nombre, contraseña y botón ENTRAR', () => {
    render(<Login />, { wrapper: MemoryRouter })
    expect(screen.getByRole('textbox')).toBeTruthy()
    expect(document.querySelector('input[type="password"]')).toBeTruthy()
    expect(screen.getByRole('button', { name: /ENTRAR/i })).toBeTruthy()
  })

  it('al enviar con credenciales correctas llama login y navega', async () => {
    mockLogin.mockResolvedValue({ access_token: 't', user_id: 1, user_name: 'u' })

    render(<Login />, { wrapper: MemoryRouter })
    const nameInput = screen.getByRole('textbox')
    const passwordInput = document.querySelector('input[type="password"]')
    fireEvent.change(nameInput, { target: { value: 'admin' } })
    fireEvent.change(passwordInput, { target: { value: 'admin' } })
    fireEvent.click(screen.getByRole('button', { name: /ENTRAR/i }))

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('admin', 'admin')
    })
    await waitFor(() => {
      expect(mockDoLogin).toHaveBeenCalledWith(expect.any(Object))
    })
  })

  it('muestra botón REGISTRAR al cambiar a crear cuenta', () => {
    render(<Login />, { wrapper: MemoryRouter })
    act(() => { fireEvent.click(screen.getByRole('button', { name: /Crear cuenta/i })) })
    expect(screen.getByRole('button', { name: /REGISTRAR/i })).toBeTruthy()
  })

  it('llama register al enviar en modo registro', async () => {
    mockRegister.mockResolvedValue({ access_token: 't', user_id: 1, user_name: 'newuser' })

    render(<Login />, { wrapper: MemoryRouter })
    fireEvent.click(screen.getByRole('button', { name: /Crear cuenta/i }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'newuser' } })
    fireEvent.change(document.querySelector('input[type="password"]'), { target: { value: 'pass' } })
    fireEvent.click(screen.getByRole('button', { name: /REGISTRAR/i }))

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith('newuser', 'pass')
    })
  })
})
