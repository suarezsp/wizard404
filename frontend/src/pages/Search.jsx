/**
 * Search.jsx - Buscar en documentos indexados; tabla de resultados con enlace a detalle.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { useToast } from '../context/ToastContext'
import { friendlyMessage } from '../utils/toastMessages'
import { searchDocuments } from '../api/client'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Table } from '../components/ui/Table'
import { AnimatedView } from '../components/AnimatedView'

export function Search() {
  const { token } = useAuth()
  const { sayForScene } = useMage()
  const { addToast } = useToast()
  const [query, setQuery] = useState('')
  const [semantic, setSemantic] = useState(false)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  useEffect(() => {
    sayForScene('search')
  }, [sayForScene])

  const doSearch = async () => {
    setLoading(true)
    setHasSearched(true)
    try {
      const data = await searchDocuments(token, { q: query, ...(semantic && { semantic: true }) })
      setResults(data)
    } catch (err) {
      setResults([])
      addToast(friendlyMessage(err.message) || 'Error al buscar', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatedView className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-6 border-b-2 border-[var(--pixel-border)] pb-4">
        <Link to="/" className="link-back-menu">
          ← Volver al menú
        </Link>
      </header>
      <h1 className="text-lg text-[var(--pixel-accent)] mb-4">Buscar entre los archivos anadidos</h1>
      <div className="flex gap-2 flex-wrap mb-4 items-center">
        <Input
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && doSearch()}
          className="flex-1 min-w-[200px]"
        />
        <label className="flex items-center gap-2 text-xs text-[var(--pixel-muted)] cursor-pointer">
          <input
            type="checkbox"
            checked={semantic}
            onChange={(e) => setSemantic(e.target.checked)}
            className="w-4 h-4 accent-[var(--pixel-accent)]"
          />
          Busqueda semantica
        </label>
        <Button onClick={doSearch} disabled={loading} className="px-4 py-2">
          BUSCAR
        </Button>
      </div>
      {loading ? (
        <p className="text-[var(--pixel-muted)] text-xs">Cargando...</p>
      ) : !hasSearched ? (
        <p className="text-[var(--pixel-muted)] text-xs">Escribe palabras y pulsa BUSCAR para buscar en el indice.</p>
      ) : (
        <div
          className="results-block border-4 border-[var(--pixel-border)] overflow-hidden animate-view-in"
          style={{
            backgroundColor: 'var(--pixel-results-bg)',
            color: 'var(--pixel-results-text)',
          }}
        >
          <Table
            staggerRows
            columns={[
              { key: 'name', label: 'Nombre' },
              { key: 'mime_type', label: 'Tipo' },
              { key: 'size_bytes', label: 'Tamaño', align: 'right' },
              { key: 'snippet', label: 'Snippet' },
            ]}
            data={results}
            emptyMessage="No hay resultados. Cambia la busqueda o importa documentos."
            renderCell={(key, value, row) => {
              if (key === 'name')
                return row.id ? (
                  <span>
                    <Link to={`/documents/${row.id}`} state={{ fromSearch: true }} className="text-[var(--pixel-accent)] hover:underline">
                      {row.name}
                    </Link>
                    {' · '}
                    <Link to={`/documents/${row.id}`} state={{ fromSearch: true }} className="text-xs opacity-80 hover:underline">
                      Ver contenido
                    </Link>
                  </span>
                ) : (
                  row.name
                )
              if (key === 'size_bytes') return value?.toLocaleString() ?? ''
              if (key === 'snippet') return <span className="max-w-md block text-xs break-words whitespace-pre-wrap">{value || '-'}</span>
              return key === 'mime_type' ? <span className="opacity-80">{value}</span> : value
            }}
          />
        </div>
      )}
    </AnimatedView>
  )
}
