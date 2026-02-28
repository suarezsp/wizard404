/**
 * App.test.jsx - Tests del componente raíz.
 */
import { describe, it, expect } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { AuthProvider } from './hooks/useAuth'
import App from './App'

function TestWrapper({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

describe('App', () => {
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
})
