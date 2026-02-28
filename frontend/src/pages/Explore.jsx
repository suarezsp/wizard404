/**
 * Explore.jsx - Lista paginada del indice; click a detalle de documento.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { listDocuments } from '../services/api'
import { Button } from '../components/ui/Button'
import { Table } from '../components/ui/Table'
import { AnimatedView } from '../components/AnimatedView'

const LIMIT = 50

export function Explore() {
  const { token } = useAuth()
  const { sayForScene } = useMage()
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    sayForScene('explore')
  }, [sayForScene])

  const load = async (off = 0) => {
    setLoading(true)
    setError('')
    try {
      const data = await listDocuments(token, { limit: LIMIT, offset: off })
      setDocs(data)
    } catch (err) {
      setDocs([])
      setError(err.message || 'Error al cargar')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(offset)
  }, [offset])

  return (
    <AnimatedView className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-6 border-b-2 border-[var(--pixel-border)] pb-4">
        <Link to="/" className="link-back-menu">
          Volver al menú
        </Link>
      </header>
      <h1 className="pixel-page-title mb-4">Explore documents</h1>
      {error && <p className="text-red-600 text-xs mb-2">{error}</p>}
      {loading ? (
        <p className="text-[var(--pixel-text-muted)] text-xs">Cargando...</p>
      ) : (
        <>
          <Table
            staggerRows
            columns={[
              { key: 'name', label: 'Nombre' },
              { key: 'mime_type', label: 'Tipo' },
              { key: 'size_bytes', label: 'Tamaño', align: 'right' },
              { key: 'snippet', label: 'Snippet' },
            ]}
            data={docs}
            emptyMessage="No hay documentos indexados. Importa una ruta desde Import para anadir al indice."
            renderCell={(key, value, row) => {
              if (key === 'name')
                return row.id ? (
                  <Link to={`/documents/${row.id}`} className="text-[var(--pixel-accent)] hover:underline">
                    {row.name}
                  </Link>
                ) : (
                  row.name
                )
              if (key === 'size_bytes') return value?.toLocaleString() ?? ''
              if (key === 'snippet') return <span className="max-w-[200px] truncate block">{value || '-'}</span>
              return key === 'mime_type' ? <span className="text-[var(--pixel-text-muted)]">{value}</span> : value
            }}
          />
          <div className="flex gap-2 mt-4">
            <Button
              variant="secondary"
              disabled={offset === 0}
              onClick={() => setOffset((o) => Math.max(0, o - LIMIT))}
              className="px-3 py-1"
            >
              ANTERIOR
            </Button>
            <Button
              variant="secondary"
              disabled={docs.length < LIMIT}
              onClick={() => setOffset((o) => o + LIMIT)}
              className="px-3 py-1"
            >
              SIGUIENTE
            </Button>
          </div>
        </>
      )}
    </AnimatedView>
  )
}
