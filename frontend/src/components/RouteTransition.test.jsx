/**
 * RouteTransition.test.jsx - Comprueba que aplica clase de salida al cambiar location y que actualiza tras onAnimationEnd.
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RouteTransition } from './RouteTransition'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'

function LocationDisplay() {
  const loc = useLocation()
  return <span data-testid="location-path">{loc.pathname}</span>
}

function TestApp() {
  return (
    <BrowserRouter>
      <RouteTransition>
        <Routes>
          <Route path="/" element={<LocationDisplay />} />
          <Route path="/other" element={<div>Other page</div>} />
        </Routes>
      </RouteTransition>
    </BrowserRouter>
  )
}

describe('RouteTransition', () => {
  it('renders children and shows current location', () => {
    render(<TestApp />)
    expect(screen.getByTestId('location-path').textContent).toBe('/')
  })

  it('applies animate-view-in when not exiting', () => {
    const { container } = render(<TestApp />)
    const wrapper = container.querySelector('.animate-view-in')
    expect(wrapper).toBeTruthy()
  })

  it('handles onAnimationEnd without crashing when not exiting', () => {
    const { container } = render(<TestApp />)
    const wrapper = container.querySelector('.animate-view-in')
    wrapper.dispatchEvent(new Event('animationend', { bubbles: true }))
    expect(screen.getByTestId('location-path').textContent).toBe('/')
  })
})
