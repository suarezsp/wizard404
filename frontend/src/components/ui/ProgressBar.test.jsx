/**
 * ProgressBar.test.jsx - Tests del componente ProgressBar (render, porcentaje, indeterminado).
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressBar } from './ProgressBar'

describe('ProgressBar', () => {
  it('renderiza con porcentaje 0', () => {
    render(<ProgressBar percent={0} />)
    const bar = screen.getByRole('progressbar')
    expect(bar).toBeTruthy()
    expect(bar.getAttribute('aria-valuenow')).toBe('0')
    expect(screen.getByText('0%')).toBeTruthy()
  })

  it('renderiza con porcentaje 50', () => {
    render(<ProgressBar percent={50} />)
    expect(screen.getByRole('progressbar').getAttribute('aria-valuenow')).toBe('50')
    expect(screen.getByText('50%')).toBeTruthy()
  })

  it('renderiza con porcentaje 100', () => {
    render(<ProgressBar percent={100} />)
    expect(screen.getByRole('progressbar').getAttribute('aria-valuenow')).toBe('100')
    expect(screen.getByText('100%')).toBeTruthy()
  })

  it('clampa porcentaje mayor a 100', () => {
    render(<ProgressBar percent={150} />)
    expect(screen.getByRole('progressbar').getAttribute('aria-valuenow')).toBe('100')
  })

  it('clampa porcentaje menor a 0', () => {
    render(<ProgressBar percent={-10} />)
    expect(screen.getByRole('progressbar').getAttribute('aria-valuenow')).toBe('0')
  })

  it('modo indeterminado no muestra porcentaje', () => {
    render(<ProgressBar indeterminate />)
    const bar = screen.getByRole('progressbar')
    expect(bar.getAttribute('aria-valuenow')).toBeFalsy()
    expect(screen.queryByText(/%/)).toBeFalsy()
  })

  it('muestra label cuando se pasa', () => {
    render(<ProgressBar percent={0} label="Escaneando..." />)
    expect(screen.getByText('Escaneando...')).toBeTruthy()
  })
})
