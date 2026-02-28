/**
 * Scan.test.jsx - Tests de la pagina Scan (barra de progreso al escanear).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ToastProvider } from '../context/ToastContext'
import { Scan } from './Scan'

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
  useMage: () => ({ sayForScene: vi.fn(), say: vi.fn() }),
}))

const mockScanDirectory = vi.fn()
const mockScanDirectoryFiles = vi.fn()
vi.mock('../api/client', () => ({
  scanDirectory: (...args) => mockScanDirectory(...args),
  scanDirectoryFiles: (...args) => mockScanDirectoryFiles(...args),
}))

describe('Scan', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.showDirectoryPicker = undefined
  })

  it('muestra barra de progreso mientras escanea servidor', async () => {
    let resolveScan
    mockScanDirectory.mockReturnValue(new Promise((r) => { resolveScan = r }))

    render(<Scan />, { wrapper: TestWrapper })

    const input = screen.getByPlaceholderText(/Ruta en el servidor/)
    fireEvent.change(input, { target: { value: '/tmp' } })
    const scanBtn = screen.getByRole('button', { name: /ESCANEAR SERVIDOR/i })
    fireEvent.click(scanBtn)

    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeTruthy()
    })
    expect(screen.getByText(/Escaneando.../i)).toBeTruthy()

    resolveScan({ total_files: 10, total_size: 1000, by_extension: {}, by_type: {} })
    await waitFor(() => {
      expect(screen.getByText(/Archivos: 10/)).toBeTruthy()
    })
  })

  it('muestra resultados tras escaneo exitoso', async () => {
    mockScanDirectory.mockResolvedValue({
      total_files: 5,
      total_size: 2048,
      by_extension: { '.txt': 3, '.pdf': 2 },
      by_type: {},
    })

    render(<Scan />, { wrapper: TestWrapper })

    fireEvent.change(screen.getByPlaceholderText(/Ruta en el servidor/), { target: { value: '/data' } })
    fireEvent.click(screen.getByRole('button', { name: /ESCANEAR SERVIDOR/i }))

    await waitFor(() => {
      expect(screen.getByText('Resultados')).toBeTruthy()
      expect(screen.getByText(/Archivos: 5/)).toBeTruthy()
      expect(screen.getByText(/\.txt: 3/)).toBeTruthy()
      expect(screen.getByText(/\.pdf: 2/)).toBeTruthy()
    })
  })

  it('al clicar en extension carga lista de archivos del servidor', async () => {
    mockScanDirectory.mockResolvedValue({
      total_files: 2,
      total_size: 100,
      by_extension: { '.txt': 2 },
      by_type: {},
    })
    mockScanDirectoryFiles.mockResolvedValue([
      { name: 'a.txt', path: '/tmp/a.txt', size_bytes: 50, mime_type: 'text/plain' },
      { name: 'b.txt', path: '/tmp/b.txt', size_bytes: 50, mime_type: 'text/plain' },
    ])

    render(<Scan />, { wrapper: TestWrapper })
    fireEvent.change(screen.getByPlaceholderText(/Ruta en el servidor/), { target: { value: '/tmp' } })
    fireEvent.click(screen.getByRole('button', { name: /ESCANEAR SERVIDOR/i }))

    await waitFor(() => { expect(screen.getByText(/\.txt: 2/)).toBeTruthy() })
    fireEvent.click(screen.getByText(/\.txt: 2/))

    await waitFor(() => {
      expect(mockScanDirectoryFiles).toHaveBeenCalledWith('fake-token', '/tmp', '.txt')
      expect(screen.getByText('Archivos .txt')).toBeTruthy()
      expect(screen.getByText('a.txt')).toBeTruthy()
      expect(screen.getByText('b.txt')).toBeTruthy()
    })
  })
})
