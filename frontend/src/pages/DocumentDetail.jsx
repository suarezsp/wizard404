/**
 * DocumentDetail.jsx - Detalle de un documento.
 * Metadatos, resumen automatico (si existe) y preview del contenido.
 */
import { useState, useEffect } from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { getDocument, getDocumentSummary } from '../services/api'
import { Card } from '../components/ui/Card'

export function DocumentDetail() {
  const { id } = useParams()
  const location = useLocation()
  const { token } = useAuth()
  const { sayForScene } = useMage()
  const fromSearch = location.state?.fromSearch
  const [doc, setDoc] = useState(null)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (doc) sayForScene('documentDetail')
    else sayForScene('loading')
  }, [doc, sayForScene])

  useEffect(() => {
    let cancelled = false
    getDocument(token, id)
      .then((d) => {
        if (!cancelled) setDoc(d)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Documento no encontrado')
      })
    getDocumentSummary(token, id)
      .then((s) => {
        if (!cancelled && s?.summary) setSummary(s.summary)
      })
      .catch(() => { /* opcional: sin resumen */ })
    return () => { cancelled = true }
  }, [token, id])

  if (error) return <p className="p-6 text-red-500">{error}</p>
  if (!doc) return <p className="p-6 text-[var(--pixel-text-muted)]">Cargando...</p>

  return (
    <div className="min-h-screen p-6">
      <header className="mb-6">
        {fromSearch ? (
          <Link to="/search" state={{ fromSearch: true }} className="text-[var(--pixel-accent)] text-xs hover:underline">
            Volver a resultados
          </Link>
        ) : (
          <Link to="/" className="text-[var(--pixel-accent)] text-xs hover:underline">
            ← Volver
          </Link>
        )}
      </header>
      <Card className="p-6">
        <h1 className="pixel-page-title mb-4">
          {doc.name}
        </h1>
        <div className="grid grid-cols-2 gap-4 text-xs mb-6 text-[var(--pixel-text-on-dark)]">
          {doc.title && (
            <div className="col-span-2">
              <span className="text-[var(--pixel-text-muted)]">Titulo:</span> {doc.title}
            </div>
          )}
          {doc.author && (
            <div className="col-span-2">
              <span className="text-[var(--pixel-text-muted)]">Autor:</span> {doc.author}
            </div>
          )}
          <div>
            <span className="text-[var(--pixel-text-muted)]">Tipo:</span> {doc.mime_type}
          </div>
          <div>
            <span className="text-[var(--pixel-text-muted)]">Tamano:</span>{' '}
            {doc.size_bytes?.toLocaleString()} bytes
          </div>
          <div className="col-span-2">
            <span className="text-[var(--pixel-text-muted)]">Ruta:</span> {doc.path}
          </div>
        </div>
        {summary && (
          <div className="border-2 border-[var(--pixel-border)] p-4 mb-6">
            <h2 className="pixel-section-title mb-2">SUMMARY</h2>
            <p className="text-xs text-[var(--pixel-text-on-dark)] whitespace-pre-wrap">
              {summary}
            </p>
          </div>
        )}
        <div className="border-2 border-[var(--pixel-border)] p-4">
          <h2 className="pixel-section-title mb-2">CONTENIDO</h2>
          <pre className="text-xs text-[var(--pixel-text-on-dark)] whitespace-pre-wrap font-mono overflow-x-auto max-h-96 overflow-y-auto">
            {doc.content_preview || '(sin contenido)'}
          </pre>
        </div>
      </Card>
    </div>
  )
}
