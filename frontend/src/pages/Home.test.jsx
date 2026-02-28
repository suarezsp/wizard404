/**
 * Home.test.jsx - Tests del menu principal (tarjetas tipo CLI).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Home } from './Home'

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: { name: 'testuser' },
    logout: vi.fn(),
  }),
}))
vi.mock('../context/MageContext', () => ({
  useMage: () => ({ sayForScene: vi.fn() }),
}))

describe('Home', () => {
  it('muestra las 6 opciones del menu y Salir', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )
    expect(screen.getByText('Scan directory')).toBeTruthy()
    expect(screen.getByText('Import documents')).toBeTruthy()
    expect(screen.getByText('Search')).toBeTruthy()
    expect(screen.getByText('Explore documents')).toBeTruthy()
    expect(screen.getByText('Organize files')).toBeTruthy()
    expect(screen.getByText('Cleanup')).toBeTruthy()
    expect(screen.getByText('SALIR')).toBeTruthy()
  })

  it('enlaza cada tarjeta a su ruta', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )
    const links = screen.getAllByRole('link')
    const hrefs = links.map((l) => l.getAttribute('href'))
    expect(hrefs).toContain('/scan')
    expect(hrefs).toContain('/import')
    expect(hrefs).toContain('/search')
    expect(hrefs).toContain('/explore')
    expect(hrefs).toContain('/organize')
    expect(hrefs).toContain('/cleanup')
  })
})
