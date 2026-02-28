/**
 * ParticleBackground.test.jsx - Comprueba que renderiza N asteriscos y que el contenedor no recibe eventos.
 */
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { ParticleBackground } from './ParticleBackground'

describe('ParticleBackground', () => {
  it('renders many asterisk particles', () => {
    const { container } = render(<ParticleBackground />)
    const particles = container.querySelectorAll('.particle-asterisk')
    expect(particles.length).toBeGreaterThanOrEqual(25)
    expect(particles.length).toBeLessThanOrEqual(40)
    particles.forEach((el) => {
      expect(el.textContent).toBe('*')
    })
  })

  it('has pointer-events none so it does not block interaction', () => {
    const { container } = render(<ParticleBackground />)
    const wrapper = container.firstChild
    expect(wrapper.className).toContain('pointer-events-none')
  })

  it('is fixed and has aria-hidden', () => {
    const { container } = render(<ParticleBackground />)
    const wrapper = container.firstChild
    expect(wrapper.className).toContain('fixed')
    expect(wrapper.className).toContain('inset-0')
    expect(wrapper.getAttribute('aria-hidden')).toBe('true')
  })
})
