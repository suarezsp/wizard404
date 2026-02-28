/**
 * Import.test.jsx - Tests de la página Import (render, envío por ruta).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ToastProvider } from '../context/ToastContext'
import { Import } from './Import'

function TestWrapper({ children }) {
  return (
    <MemoryRouter>
      <ToastProvider>{children}</ToastProvider>
    </MemoryRouter>
  )
}

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ token: 'fake-token' }),
}))
vi.mock('../context/MageContext', () => ({
  useMage: () => ({ sayForScene: vi.fn() }),
}))

const mockImportPath = vi.fn()
const mockUploadDocuments = vi.fn()
vi.mock('../services/api', () => ({
  importPath: (...args) => mockImportPath(...args),
  uploadDocuments: (...args) => mockUploadDocuments(...args),
}))

describe('Import', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.showDirectoryPicker = undefined
  })

  it('renderiza título y campo de ruta', () => {
    render(<Import />, { wrapper: TestWrapper })
    expect(screen.getByText(/Import documents/i)).toBeTruthy()
    expect(screen.getByPlaceholderText(/Ruta en el servidor/)).toBeTruthy()
    expect(screen.getByRole('button', { name: /IMPORTAR SERVIDOR/i })).toBeTruthy()
  })

  it('envía import por ruta al pulsar IMPORTAR SERVIDOR', async () => {
    mockImportPath.mockResolvedValue({ imported: 3 })

    render(<Import />, { wrapper: TestWrapper })
    fireEvent.change(screen.getByPlaceholderText(/Ruta en el servidor/), { target: { value: '/tmp/docs' } })
    fireEvent.click(screen.getByRole('button', { name: /IMPORTAR SERVIDOR/i }))

    await waitFor(() => {
      expect(mockImportPath).toHaveBeenCalledWith('fake-token', '/tmp/docs')
    })
    await waitFor(() => {
      expect(screen.getByText(/Importados: 3/)).toBeTruthy()
    })
  })

  it('muestra estado de carga mientras importa', async () => {
    let resolveImport
    mockImportPath.mockReturnValue(new Promise((r) => { resolveImport = r }))

    render(<Import />, { wrapper: TestWrapper })
    fireEvent.change(screen.getByPlaceholderText(/Ruta en el servidor/), { target: { value: '/tmp' } })
    fireEvent.click(screen.getByRole('button', { name: /IMPORTAR SERVIDOR/i }))

    await waitFor(() => {
      expect(screen.getByText(/IMPORTANDO/)).toBeTruthy()
    })
    resolveImport({ imported: 0 })
    await waitFor(() => {
      expect(screen.queryByText(/IMPORTANDO/)).toBeFalsy()
    })
  })
})
