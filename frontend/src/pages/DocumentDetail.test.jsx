/**
 * DocumentDetail.test.jsx - Tests del detalle de documento.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { DocumentDetail } from './DocumentDetail'

vi.mock('../hooks/useAuth', () => ({ useAuth: () => ({ token: 'fake-token' }) }))
vi.mock('../context/MageContext', () => ({ useMage: () => ({ sayForScene: vi.fn() }) }))
const mockGetDocument = vi.fn()
const mockGetDocumentSummary = vi.fn()
vi.mock('../api/client', () => ({
  getDocument: (...args) => mockGetDocument(...args),
  getDocumentSummary: (...args) => mockGetDocumentSummary(...args),
}))

describe('DocumentDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetDocumentSummary.mockResolvedValue({})
  })

  it('muestra cargando mientras obtiene el documento', () => {
    mockGetDocument.mockReturnValue(new Promise(() => {}))
    render(
      <MemoryRouter initialEntries={['/documents/1']}>
        <Routes>
          <Route path="/documents/:id" element={<DocumentDetail />} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText(/Cargando/)).toBeTruthy()
  })

  it('renderiza nombre y metadatos cuando el documento existe', async () => {
    mockGetDocument.mockResolvedValue({
      id: 1,
      name: 'contrato.pdf',
      path: '/storage/contrato.pdf',
      mime_type: 'application/pdf',
      size_bytes: 4096,
      content_preview: 'Texto del contrato...',
    })
    render(
      <MemoryRouter initialEntries={['/documents/1']}>
        <Routes>
          <Route path="/documents/:id" element={<DocumentDetail />} />
        </Routes>
      </MemoryRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('contrato.pdf')).toBeTruthy()
      expect(screen.getByText(/application\/pdf/)).toBeTruthy()
      expect(screen.getByText(/Texto del contrato/)).toBeTruthy()
    })
  })

  it('muestra enlace Volver a resultados cuando fromSearch', async () => {
    mockGetDocument.mockResolvedValue({
      id: 1,
      name: 'doc.pdf',
      path: '/x',
      mime_type: 'application/pdf',
      size_bytes: 0,
      content_preview: '',
    })
    render(
      <MemoryRouter initialEntries={[{ pathname: '/documents/1', state: { fromSearch: true } }]}>
        <Routes>
          <Route path="/documents/:id" element={<DocumentDetail />} />
        </Routes>
      </MemoryRouter>
    )
    await waitFor(() => { expect(screen.getByText('doc.pdf')).toBeTruthy() })
    const link = screen.getByRole('link', { name: /Volver a resultados/i })
    expect(link).toBeTruthy()
    expect(link.getAttribute('href')).toBe('/search')
  })

  it('muestra error cuando el documento no se encuentra', async () => {
    mockGetDocument.mockRejectedValue(new Error('Not found'))
    render(
      <MemoryRouter initialEntries={['/documents/1']}>
        <Routes>
          <Route path="/documents/:id" element={<DocumentDetail />} />
        </Routes>
      </MemoryRouter>
    )
    await waitFor(() => { expect(screen.getByText(/Documento no encontrado|Not found/)).toBeTruthy() })
  })
})
