/**
 * CRTToggleButton.test.jsx - Comprueba toggle, aria y llamada a onToggle.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CRTToggleButton } from './CRTToggleButton'

describe('CRTToggleButton', () => {
  it('renderiza con active true y aria-pressed', () => {
    render(<CRTToggleButton active onToggle={() => {}} />)
    const btn = screen.getByTestId('crt-toggle')
    expect(btn.getAttribute('aria-pressed')).toBe('true')
    expect(btn.getAttribute('aria-label')).toBe('Desactivar efecto pantalla CRT')
  })

  it('renderiza con active false y aria-pressed', () => {
    render(<CRTToggleButton active={false} onToggle={() => {}} />)
    const btn = screen.getByTestId('crt-toggle')
    expect(btn.getAttribute('aria-pressed')).toBe('false')
    expect(btn.getAttribute('aria-label')).toBe('Activar efecto pantalla CRT')
  })

  it('llama a onToggle una vez al hacer click', () => {
    const onToggle = vi.fn()
    render(<CRTToggleButton active={false} onToggle={onToggle} />)
    fireEvent.click(screen.getByTestId('crt-toggle'))
    expect(onToggle).toHaveBeenCalledTimes(1)
  })
})
