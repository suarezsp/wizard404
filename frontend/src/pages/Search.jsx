/**
 * Search.jsx - Buscar en documentos indexados; tabla de resultados con enlace a detalle.
 * Incluye highlight de terminos de busqueda en el snippet y orden por fecha/tamano.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { useToast } from '../context/ToastContext'
import { friendlyMessage } from '../utils/toastMessages'
import { searchDocuments, reindexEmbeddings } from '../services/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Table } from '../components/ui/Table'
import { AnimatedView } from '../components/AnimatedView'

function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/** Devuelve JSX con los terminos de query resaltados en el snippet (highlight). */
function HighlightSnippet({ snippet, query }) {
  const text = snippet || ''
  const tokens = query.trim().split(/\s+/).filter(Boolean)
  if (!tokens.length) return <span className="max-w-md block text-xs break-words whitespace-pre-wrap">{text || '-'}</span>
  const re = new RegExp('(' + tokens.map(escapeRegex).join('|') + ')', 'gi')
  const parts = text.split(re)
  return (
    <span className="max-w-md block text-xs break-words whitespace-pre-wrap">
      {parts.map((p, i) =>
        i % 2 === 1 ? (
          <mark key={i} className="bg-[var(--pixel-accent)]/30 rounded-sm px-0.5">{p}</mark>
        ) : (
          <span key={i}>{p}</span>
        )
      )}
    </span>
  )
}

export function Search() {
  const { token } = useAuth()
  const { sayForScene } = useMage()
  const { addToast } = useToast()
  const [query, setQuery] = useState('')
  const [semantic, setSemantic] = useState(false)
  const [orderBy, setOrderBy] = useState('modified_at')
  const [results, setResults] = useState([])
  const [semanticUsed, setSemanticUsed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [reindexing, setReindexing] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  useEffect(() => {
    sayForScene('search')
  }, [sayForScene])

  const doSearch = async () => {
    setLoading(true)
    setHasSearched(true)
    try {
      const params = { q: query, ...(semantic && { semantic: true }), order_by: orderBy, order_desc: true }
      const { results: data, semanticUsed: used } = await searchDocuments(token, params)
      setResults(data)
      setSemanticUsed(used)
    } catch (err) {
      setResults([])
      setSemanticUsed(false)
      addToast(friendlyMessage(err.message) || 'Error al buscar', 'error')
    } finally {
      setLoading(false)
    }
  }

  const doReindex = async () => {
    setReindexing(true)
    try {
      const { reindexed } = await reindexEmbeddings(token)
      addToast(`Embeddings reindexados: ${reindexed} documentos`, 'success')
    } catch (err) {
      addToast(friendlyMessage(err.message) || 'Error al reindexar', 'error')
    } finally {
      setReindexing(false)
    }
  }

  return (
    <AnimatedView className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-6 border-b-2 border-[var(--pixel-border)] pb-4">
        <Link to="/" className="link-back-menu">
          Volver al menú
        </Link>
      </header>
      <h1 className="pixel-page-title mb-4">Buscar entre los archivos anadidos</h1>
      <div className="flex gap-2 flex-wrap mb-4 items-center">
        <Input
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && doSearch()}
          className="flex-1 min-w-[200px]"
        />
        <label className="flex items-center gap-2 text-xs text-[var(--pixel-text-muted)]">
          Ordenar por:
        </label>
        <select
          value={orderBy}
          onChange={(e) => setOrderBy(e.target.value)}
          className="border-2 border-[var(--pixel-border)] bg-[var(--pixel-panel)] text-[var(--pixel-text-on-dark)] text-xs px-2 py-1"
        >
          <option value="modified_at">Fecha</option>
          <option value="size">Tamano</option>
          <option value="name">Nombre</option>
        </select>
        <label className="flex items-center gap-2 text-xs text-[var(--pixel-text-muted)] cursor-pointer" title="Por similitud de significado (recomendado para conceptos)">
          <input
            type="checkbox"
            checked={semantic}
            onChange={(e) => setSemantic(e.target.checked)}
            className="w-4 h-4 accent-[var(--pixel-accent)]"
          />
          Busqueda semantica
          <span className="hidden sm:inline opacity-70">(por significado)</span>
        </label>
        <Button onClick={doSearch} disabled={loading} className="px-4 py-2">
          BUSCAR
        </Button>
        <Button onClick={doReindex} disabled={reindexing} className="px-4 py-2" title="Recalcular vectores para busqueda semantica (util si no varia con la consulta)">
          Reindexar embeddings
        </Button>
      </div>
      {hasSearched && semantic && (
        <p className="text-xs mb-2 text-[var(--pixel-text-muted)]">
          {semanticUsed
            ? 'Ordenado por similitud con la consulta.'
            : 'Ordenado por fecha (busqueda por vectores no disponible; instale sentence-transformers o pulse Reindexar embeddings).'}
        </p>
      )}
      {loading ? (
        <p className="text-[var(--pixel-text-muted)] text-xs">Cargando...</p>
      ) : !hasSearched ? (
        <p className="text-[var(--pixel-text-muted)] text-xs">Escribe palabras y pulsa BUSCAR para buscar en el indice.</p>
      ) : (
        <div
          className="results-block border-4 border-[var(--pixel-border)] rounded-none overflow-hidden animate-view-in"
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
              if (key === 'snippet') return <HighlightSnippet snippet={value} query={query} />
              return key === 'mime_type' ? <span className="opacity-80">{value}</span> : value
            }}
          />
        </div>
      )}
    </AnimatedView>
  )
}
