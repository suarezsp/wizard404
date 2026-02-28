/**
 * CRTOverlay.test.jsx - Comprueba que el overlay no bloquea interaccion y tiene z-index.
 */
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { CRTOverlay } from './CRTOverlay'

describe('CRTOverlay', () => {
  it('renderiza sin fallos', () => {
    const { container } = render(<CRTOverlay />)
    expect(container.firstChild).toBeTruthy()
  })

  it('tiene pointer-events-none', () => {
    const { container } = render(<CRTOverlay />)
    const el = container.firstChild
    expect(el.className).toContain('pointer-events-none')
  })

  it('tiene z-index 90 y aria-hidden', () => {
    const { container } = render(<CRTOverlay />)
    const el = container.firstChild
    expect(el.style.zIndex).toBe('90')
    expect(el.getAttribute('aria-hidden')).toBe('true')
  })
})
