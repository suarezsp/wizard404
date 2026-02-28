/**
 * client.test.js - Tests del cliente API con fetch mockeado.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  healthCheck,
  login,
  listDocuments,
  getDocumentSummary,
  scanDirectory,
} from './client'

const base = 'http://localhost:8000'

describe('api/client', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it('healthCheck devuelve datos cuando el backend responde ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', database: 'ready' }),
    })
    const res = await healthCheck()
    expect(fetch).toHaveBeenCalledWith(`${base}/health`)
    expect(res).toEqual({ status: 'ok', database: 'ready' })
  })

  it('healthCheck devuelve error cuando el backend no esta disponible', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))
    const res = await healthCheck()
    expect(res).toEqual({ error: 'Network error' })
  })

  it('healthCheck devuelve error cuando responde !ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      statusText: 'Service Unavailable',
      json: () => Promise.resolve({ detail: 'DB down' }),
    })
    const res = await healthCheck()
    expect(res).toEqual({ error: 'DB down' })
  })

  it('login lanza Error con detail del backend cuando falla', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      statusText: 'Unauthorized',
      json: () => Promise.resolve({ detail: 'Invalid credentials' }),
    })
    await expect(login('u', 'p')).rejects.toThrow('Invalid credentials')
  })

  it('login devuelve datos cuando responde ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ access_token: 't', user: { name: 'u' } }),
    })
    const res = await login('u', 'p')
    expect(res).toEqual({ access_token: 't', user: { name: 'u' } })
    expect(fetch).toHaveBeenCalledWith(
      `${base}/auth/login`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ name: 'u', password: 'p' }),
      })
    )
  })

  it('listDocuments envia token y params y devuelve array', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([{ id: 1, name: 'a' }]),
    })
    const res = await listDocuments('tk', { limit: 10, offset: 0 })
    expect(res).toEqual([{ id: 1, name: 'a' }])
    expect(fetch).toHaveBeenCalledWith(
      `${base}/documents?limit=10&offset=0`,
      expect.objectContaining({ headers: { Authorization: 'Bearer tk' } })
    )
  })

  it('getDocumentSummary devuelve summary cuando responde ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ summary: 'Resumen aqui', doc_id: 1 }),
    })
    const res = await getDocumentSummary('tk', 1)
    expect(res).toEqual({ summary: 'Resumen aqui', doc_id: 1 })
    expect(fetch).toHaveBeenCalledWith(
      `${base}/documents/1/summary`,
      expect.objectContaining({ headers: { Authorization: 'Bearer tk' } })
    )
  })

  it('getDocumentSummary lanza con detail cuando backend devuelve error', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      statusText: 'Not Found',
      json: () => Promise.resolve({ detail: 'Document not found' }),
    })
    await expect(getDocumentSummary('tk', 99)).rejects.toThrow('Document not found')
  })

  it('scanDirectory envia token y path y devuelve stats', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          total_files: 10,
          total_size: 1024,
          by_type: { 'text/plain': 5 },
          by_extension: { '.txt': 5 },
        }),
    })
    const res = await scanDirectory('tk', '/tmp/docs')
    expect(res).toEqual({
      total_files: 10,
      total_size: 1024,
      by_type: { 'text/plain': 5 },
      by_extension: { '.txt': 5 },
    })
    expect(fetch).toHaveBeenCalledWith(
      `${base}/scan?path=${encodeURIComponent('/tmp/docs')}`,
      expect.objectContaining({ headers: { Authorization: 'Bearer tk' } })
    )
  })
})
