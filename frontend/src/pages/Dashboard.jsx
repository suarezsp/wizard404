/**
 * Dashboard.jsx - Búsqueda y lista de documentos.
 * Campo de búsqueda, filtros, tabla de resultados.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { searchDocuments, importPath } from '../services/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Table } from '../components/ui/Table'

export function Dashboard() {
  const { token, user, logout } = useAuth()
  const { sayForScene } = useMage()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [importPathVal, setImportPathVal] = useState('')
  const [importing, setImporting] = useState(false)
  const [searchError, setSearchError] = useState('')

  useEffect(() => {
    sayForScene('dashboard')
  }, [sayForScene])

  useEffect(() => {
    if (loading) sayForScene('loading')
  }, [loading, sayForScene])

  const doSearch = async () => {
    setLoading(true)
    setSearchError('')
    try {
      const data = await searchDocuments(token, { q: query })
      setResults(data)
    } catch (err) {
      setResults([])
      setSearchError(err.message || 'Error al buscar')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    doSearch()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- solo carga inicial al montar
  }, [])

  const handleImport = async () => {
    if (!importPathVal.trim()) return
    setImporting(true)
    try {
      await importPath(token, importPathVal.trim())
      doSearch()
      setImportPathVal('')
    } catch (err) {
      alert(err.message || 'Error al importar')
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-8 border-b-2 border-[var(--pixel-border)] pb-4">
        <h1 className="pixel-page-title">WIZARD404</h1>
        <div className="flex items-center gap-4">
          <span className="pixel-subtitle text-xs">{user?.name}</span>
          <Button onClick={logout} variant="secondary" className="px-3 py-1">
            SALIR
          </Button>
        </div>
      </header>

      <div className="mb-6 flex gap-2 flex-wrap">
        <Input
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && doSearch()}
          className="flex-1 min-w-[200px]"
        />
        <Button onClick={doSearch} className="px-4 py-2">
          BUSCAR
        </Button>
      </div>

      <div className="mb-6 flex gap-2">
        <Input
          placeholder="Ruta para importar (ej: /ruta/a/docs)"
          value={importPathVal}
          onChange={(e) => setImportPathVal(e.target.value)}
          className="flex-1 min-w-[200px]"
        />
        <Button onClick={handleImport} disabled={importing} variant="secondary" className="px-4 py-2">
          IMPORTAR
        </Button>
      </div>

      {searchError && (
        <p className="text-red-500 text-xs mb-2">{searchError}</p>
      )}
      {loading ? (
        <p className="text-[var(--pixel-text-muted)] text-xs">Cargando...</p>
      ) : (
        <Table
          columns={[
            { key: 'name', label: 'Nombre' },
            { key: 'mime_type', label: 'Tipo' },
            { key: 'size_bytes', label: 'Tamaño', align: 'right' },
            { key: 'snippet', label: 'Snippet' },
          ]}
          data={results}
          emptyMessage="No hay documentos. Importa una ruta para comenzar."
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
      )}
    </div>
  )
}
