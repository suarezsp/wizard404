/**
 * CRTContentWrapper.test.jsx - Comprueba que envuelve a los hijos, aplica el filtro y el overlay redirige clics.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, fireEvent, screen } from '@testing-library/react'
import { CRTContentWrapper } from './CRTContentWrapper'

describe('CRTContentWrapper', () => {
  it('renderiza los hijos dentro del wrapper', () => {
    const { container, getByText } = render(
      <CRTContentWrapper>
        <span>Child content</span>
      </CRTContentWrapper>
    )
    expect(getByText('Child content')).toBeTruthy()
    const wrapper = container.querySelector('.crt-content-wrapper')
    expect(wrapper).toBeTruthy()
    expect(wrapper.textContent).toContain('Child content')
  })

  it('aplica el estilo filter url crt-barrel al wrapper', () => {
    const { container } = render(
      <CRTContentWrapper>
        <div />
      </CRTContentWrapper>
    )
    const wrapper = container.querySelector('.crt-content-wrapper')
    expect(wrapper).toBeTruthy()
    expect(wrapper.style.filter).toBe('url(#crt-barrel)')
  })

  it('el overlay redirige el clic al elemento logico (jsdom: mock elementFromPoint)', () => {
    let clicked = false
    const { container } = render(
      <CRTContentWrapper>
        <button type="button" onClick={() => { clicked = true }}>
          Target
        </button>
      </CRTContentWrapper>
    )
    const button = screen.getByRole('button', { name: 'Target' })
    const overlay = container.querySelector('.crt-content-wrapper-overlay')
    expect(overlay).toBeTruthy()
    const orig = document.elementFromPoint
    document.elementFromPoint = vi.fn(() => button)
    try {
      const rect = overlay.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      fireEvent.click(overlay, { clientX: centerX, clientY: centerY })
      expect(clicked).toBe(true)
    } finally {
      document.elementFromPoint = orig
    }
  })
})
