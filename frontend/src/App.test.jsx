/**
 * App.test.jsx - Tests del componente raíz y del overlay CRT.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { AuthProvider } from './hooks/useAuth'
import App from './App'

function TestWrapper({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

describe('App', () => {
  beforeEach(() => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })
  })

  it('renderiza la aplicación y muestra login cuando no hay token', async () => {
    const { container } = render(<App />, { wrapper: TestWrapper })
    const transitionWrapper = container.querySelector('.animate-view-in') ?? container.querySelector('.animate-view-out')
    if (transitionWrapper) {
      act(() => {
        transitionWrapper.dispatchEvent(new Event('animationend', { bubbles: true }))
      })
    }
    const title = await screen.findByText(/WIZARD404/i, {}, { timeout: 2000 })
    expect(title).toBeTruthy()
  })

  it('muestra el boton CRT toggle siempre', () => {
    render(<App />, { wrapper: TestWrapper })
    expect(screen.getByTestId('crt-toggle')).toBeTruthy()
  })

  it('con overlay desactivado no monta CRTContentWrapper ni CRTOverlay', () => {
    const { container } = render(<App />, { wrapper: TestWrapper })
    expect(container.querySelector('.crt-content-wrapper')).toBeFalsy()
    const overlays = container.querySelectorAll('[aria-hidden="true"]')
    const hasCrtOverlay = Array.from(overlays).some((el) => el.style.zIndex === '90')
    expect(hasCrtOverlay).toBe(false)
  })

  it('al activar el toggle se montan wrapper y overlay', () => {
    const { container } = render(<App />, { wrapper: TestWrapper })
    fireEvent.click(screen.getByTestId('crt-toggle'))
    expect(container.querySelector('.crt-content-wrapper')).toBeTruthy()
    const overlay = container.querySelector('[style*="z-index: 90"]')
    expect(overlay).toBeTruthy()
  })
})
