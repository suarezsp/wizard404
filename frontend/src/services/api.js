/**
 * services/api.js - Cliente HTTP para la API Wizard404.
 * Unico modulo que realiza llamadas al backend. Los componentes y paginas solo
 * consumen desde aqui; no deben contener logica de red ni llamar a fetch directamente.
 *
 * Endpoints: GET /health, POST /auth/login, POST /auth/register,
 * GET /documents, GET /documents/search, GET /documents/:id, GET /documents/:id/summary,
 * POST /documents/import, POST /documents/upload, GET /scan, GET /scan/files.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Lee el body JSON de la respuesta de error y extrae el mensaje (detail).
 * FastAPI devuelve { detail: string } o { detail: string[] }.
 */
async function getErrorDetail(response) {
  try {
    const data = await response.json()
    const d = data?.detail
    if (typeof d === 'string') return d
    if (Array.isArray(d) && d.length > 0) return String(d[0])
    return null
  } catch {
    return null
  }
}

/**
 * Si !response.ok, lanza Error con el detail del backend o statusText.
 */
async function throwIfNotOk(response) {
  if (response.ok) return
  const message = await getErrorDetail(response) || response.statusText
  throw new Error(message)
}

export async function healthCheck() {
  try {
    const r = await fetch(`${API_BASE}/health`)
    if (!r.ok) return { error: await getErrorDetail(r) || r.statusText }
    return r.json()
  } catch (err) {
    return { error: err.message || 'Backend unreachable' }
  }
}

export async function login(name, password) {
  const r = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, password }),
  })
  await throwIfNotOk(r)
  return r.json()
}

export async function register(name, password) {
  const r = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, password }),
  })
  await throwIfNotOk(r)
  return r.json()
}

/**
 * Lista documentos indexados del usuario. params: limit, offset (opcionales).
 * Devuelve array de { id, name, path, mime_type, size_bytes, snippet }.
 * @param {string} token - Bearer token
 * @param {{ limit?: number, offset?: number }} params
 */
export async function listDocuments(token, params = {}) {
  const q = new URLSearchParams(params).toString()
  const r = await fetch(`${API_BASE}/documents?${q}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}

/**
 * Busca en documentos indexados. params: q (texto), semantic (bool), mime_type, min_size, max_size, limit, offset.
 * Devuelve { results, semanticUsed }. results: array con id, name, path, mime_type, size_bytes, snippet.
 * semanticUsed: true si se ordeno por similitud (vectores); false si fallback (orden por fecha).
 * @param {string} token - Bearer token
 * @param {{ q?: string, semantic?: boolean, limit?: number, offset?: number }} params
 */
export async function searchDocuments(token, params = {}) {
  const q = new URLSearchParams(params).toString()
  const r = await fetch(`${API_BASE}/documents/search?${q}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  const data = await r.json()
  const semanticUsed = r.headers.get('X-Semantic-Used') === 'true'
  return { results: data, semanticUsed }
}

/**
 * Reindexa embeddings de todos los documentos del usuario (recalcula vectores con texto rico).
 * Util si la busqueda semantica no varia con la consulta. Devuelve { reindexed }.
 * @param {string} token - Bearer token
 */
export async function reindexEmbeddings(token) {
  const r = await fetch(`${API_BASE}/documents/reindex-embeddings`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}

export async function getDocument(token, id) {
  const r = await fetch(`${API_BASE}/documents/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}

/**
 * Resumen automatico del documento. Devuelve { summary, doc_id }.
 */
export async function getDocumentSummary(token, id) {
  const r = await fetch(`${API_BASE}/documents/${id}/summary`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}

export async function importPath(token, path) {
  const r = await fetch(`${API_BASE}/documents/import?path=${encodeURIComponent(path)}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}

/**
 * Sube archivos al backend (multipart). files: File[].
 * Devuelve { imported, document_ids }.
 */
export async function uploadDocuments(token, files) {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }
  const r = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  })
  await throwIfNotOk(r)
  return r.json()
}

/**
 * Escanea un directorio en el servidor. Devuelve { total_files, total_size, by_type, by_extension }.
 */
export async function scanDirectory(token, path) {
  const r = await fetch(`${API_BASE}/scan?path=${encodeURIComponent(path)}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}

/**
 * Lista archivos de un directorio escaneado en el servidor; opcionalmente por extension.
 * Devuelve array de { name, path, size_bytes, mime_type }.
 */
export async function scanDirectoryFiles(token, path, extension = '') {
  const params = new URLSearchParams({ path })
  if (extension) params.set('extension', extension.startsWith('.') ? extension : `.${extension}`)
  const r = await fetch(`${API_BASE}/scan/files?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  await throwIfNotOk(r)
  return r.json()
}
