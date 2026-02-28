/**
 * Search.test.jsx - Tests de la página Search.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ToastProvider } from '../context/ToastContext'
import { Search } from './Search'

function TestWrapper({ children }) {
  return (
    <MemoryRouter>
      <ToastProvider>{children}</ToastProvider>
    </MemoryRouter>
  )
}

vi.mock('../hooks/useAuth', () => ({ useAuth: () => ({ token: 'fake-token' }) }))
vi.mock('../context/MageContext', () => ({ useMage: () => ({ sayForScene: vi.fn() }) }))
const mockSearchDocuments = vi.fn()
vi.mock('../api/client', () => ({ searchDocuments: (...args) => mockSearchDocuments(...args) }))

describe('Search', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renderiza formulario y muestra hint sin llamar a la API hasta pulsar BUSCAR', () => {
    render(<Search />, { wrapper: TestWrapper })
    expect(screen.getByPlaceholderText(/Buscar/)).toBeTruthy()
    expect(screen.getByRole('button', { name: /BUSCAR/i })).toBeTruthy()
    expect(screen.getByText(/Escribe palabras y pulsa BUSCAR/)).toBeTruthy()
    expect(mockSearchDocuments).not.toHaveBeenCalled()
  })

  it('muestra empty state cuando no hay resultados tras buscar', async () => {
    mockSearchDocuments.mockResolvedValue([])
    render(<Search />, { wrapper: TestWrapper })
    fireEvent.click(screen.getByRole('button', { name: /BUSCAR/i }))
    await waitFor(() => { expect(screen.getByText(/No hay resultados/)).toBeTruthy() })
  })

  it('muestra resultados cuando la API devuelve datos', async () => {
    mockSearchDocuments.mockResolvedValue([
      { id: 1, name: 'doc1.pdf', mime_type: 'application/pdf', size_bytes: 1024, snippet: '...' },
    ])
    render(<Search />, { wrapper: TestWrapper })
    fireEvent.click(screen.getByRole('button', { name: /BUSCAR/i }))
    await waitFor(() => { expect(screen.getByText('doc1.pdf')).toBeTruthy() })
  })

  it('envia busqueda con query al pulsar BUSCAR', async () => {
    mockSearchDocuments.mockResolvedValue([])
    render(<Search />, { wrapper: TestWrapper })
    fireEvent.change(screen.getByPlaceholderText(/Buscar/), { target: { value: 'contrato' } })
    fireEvent.click(screen.getByRole('button', { name: /BUSCAR/i }))
    await waitFor(() => { expect(mockSearchDocuments).toHaveBeenCalledWith('fake-token', expect.objectContaining({ q: 'contrato' })) })
  })
})
