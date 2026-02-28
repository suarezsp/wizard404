/**
 * Scan.jsx - Escanear directorio: servidor (ruta) o carpeta local (File System Access API).
 * Progreso cada N archivos; evita doble picker; drill-down por extension (tabla + detalle).
 * El mago comenta segun el tipo de archivos dominante (getScanComment).
 */
import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { useToast } from '../context/ToastContext'
import { friendlyMessage } from '../utils/toastMessages'
import { scanDirectory, scanDirectoryFiles } from '../services/api'
import { getScanComment } from '../services/mageData'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card } from '../components/ui/Card'
import { ProgressBar } from '../components/ui/ProgressBar'
import { Table } from '../components/ui/Table'
import { AnimatedView } from '../components/AnimatedView'

const hasDirectoryPicker = typeof window !== 'undefined' && typeof window.showDirectoryPicker === 'function'

const PROGRESS_BAR_MAX_SECONDS = 20
const PROGRESS_BAR_TARGET = 90
const PROGRESS_UPDATE_INTERVAL_MS = 350
const PROGRESS_FILES_UPDATE_EVERY = 10

async function* walkDirectory(handle) {
  for await (const entry of handle.values()) {
    if (entry.kind === 'file') {
      const file = await entry.getFile()
      yield { name: file.name, size: file.size }
    } else if (entry.kind === 'directory') {
      yield* walkDirectory(entry)
    }
  }
}

function computeStatsFromFiles(files) {
  let total_files = 0
  let total_size = 0
  const by_extension = {}
  const filesByExtension = {}
  for (const { name, size } of files) {
    total_files += 1
    total_size += size
    const ext = name.includes('.') ? '.' + name.split('.').pop().toLowerCase() : '(sin ext)'
    by_extension[ext] = (by_extension[ext] || 0) + 1
    if (!filesByExtension[ext]) filesByExtension[ext] = []
    filesByExtension[ext].push({ name, size })
  }
  return { total_files, total_size, by_extension, by_type: {}, filesByExtension }
}

export function Scan() {
  const { token } = useAuth()
  const { sayForScene, say } = useMage()
  const { addToast } = useToast()
  const [path, setPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [filesByExtension, setFilesByExtension] = useState(null)
  const [scanPath, setScanPath] = useState(null)
  const [selectedExtension, setSelectedExtension] = useState(null)
  const [detailFile, setDetailFile] = useState(null)
  const [filesFromServer, setFilesFromServer] = useState(null)
  const [loadingFiles, setLoadingFiles] = useState(false)
  const [progressPercent, setProgressPercent] = useState(0)
  const [progressIndeterminate, setProgressIndeterminate] = useState(false)
  const [progressFiles, setProgressFiles] = useState(null)
  const progressIntervalRef = useRef(null)
  const progressStartRef = useRef(null)
  const pickerOpenRef = useRef(false)

  useEffect(() => {
    sayForScene('scan')
  }, [sayForScene])

  useEffect(() => {
    if (stats && stats.by_extension) {
      const phrase = getScanComment(stats.by_extension)
      if (phrase) say(phrase)
    }
  }, [stats])

  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current)
    }
  }, [])

  function startTimeBasedProgress() {
    setProgressPercent(0)
    setProgressIndeterminate(false)
    setProgressFiles(null)
    progressStartRef.current = Date.now()
    progressIntervalRef.current = setInterval(() => {
      const elapsed = (Date.now() - progressStartRef.current) / 1000
      const value = Math.min(PROGRESS_BAR_TARGET, Math.floor((elapsed / PROGRESS_BAR_MAX_SECONDS) * PROGRESS_BAR_TARGET))
      setProgressPercent(value)
    }, PROGRESS_UPDATE_INTERVAL_MS)
  }

  function stopProgress(complete = true) {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
      progressIntervalRef.current = null
    }
    setProgressPercent(complete ? 100 : 0)
    setProgressIndeterminate(false)
    setProgressFiles(null)
  }

  const handleScanServer = async () => {
    if (!path.trim()) {
      addToast('Indica una ruta.', 'error')
      return
    }
    setLoading(true)
    setStats(null)
    setFilesByExtension(null)
    setScanPath(path.trim())
    setSelectedExtension(null)
    setDetailFile(null)
    setFilesFromServer(null)
    startTimeBasedProgress()
    try {
      const data = await scanDirectory(token, path.trim())
      stopProgress(true)
      setStats(data)
    } catch (err) {
      stopProgress(false)
      addToast(friendlyMessage(err.message) || 'Error al escanear', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handlePickFolder = async () => {
    if (!hasDirectoryPicker) return
    if (pickerOpenRef.current) {
      addToast('Espera a que se cierre el selector de carpeta.', 'warning')
      return
    }
    setLoading(true)
    setStats(null)
    setFilesByExtension(null)
    setScanPath(null)
    setSelectedExtension(null)
    setDetailFile(null)
    setFilesFromServer(null)
    setProgressIndeterminate(true)
    setProgressFiles(0)
    pickerOpenRef.current = true
    try {
      const dir = await window.showDirectoryPicker()
      const files = []
      let count = 0
      for await (const f of walkDirectory(dir)) {
        files.push(f)
        count += 1
        if (count % PROGRESS_FILES_UPDATE_EVERY === 0) setProgressFiles(count)
      }
      setProgressIndeterminate(false)
      setProgressPercent(100)
      setProgressFiles(count)
      const result = computeStatsFromFiles(files)
      setStats(result)
      setFilesByExtension(result.filesByExtension || null)
    } catch (err) {
      if (err.name === 'AbortError') {
        setProgressIndeterminate(false)
        setProgressFiles(null)
        setLoading(false)
        pickerOpenRef.current = false
        return
      }
      setProgressIndeterminate(false)
      setProgressFiles(null)
      const msg = err.message || ''
      const isPermission = /permission|denied|system|security/i.test(msg)
      if (isPermission) {
        addToast('No se pudo acceder a esta carpeta (permisos o carpeta de sistema). Prueba otra carpeta o usa la ruta en el servidor.', 'error')
      } else {
        addToast(friendlyMessage(msg) || 'Error al leer la carpeta', 'error')
      }
    } finally {
      setLoading(false)
      pickerOpenRef.current = false
    }
  }

  const handleSelectExtension = (ext) => {
    setDetailFile(null)
    setSelectedExtension(ext)
    if (filesByExtension && filesByExtension[ext]) {
      setFilesFromServer(null)
      return
    }
    if (scanPath) {
      setLoadingFiles(true)
      scanDirectoryFiles(token, scanPath, ext)
        .then((list) => {
          setFilesFromServer(list)
        })
        .catch((err) => {
          addToast(friendlyMessage(err.message) || 'Error al cargar archivos', 'error')
          setFilesFromServer([])
        })
        .finally(() => setLoadingFiles(false))
    }
  }

  const currentFileList = selectedExtension
    ? (filesByExtension && filesByExtension[selectedExtension]) || filesFromServer || []
    : []

  const formatSize = (bytes) => (bytes != null ? `${Number(bytes).toLocaleString()} B` : '')

  return (
    <AnimatedView className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-6 border-b-2 border-[var(--pixel-border)] pb-4">
        <Link to="/" className="link-back-menu">
          Volver al menú
        </Link>
      </header>
      <h1 className="pixel-page-title mb-4">Scan directory</h1>
      <p className="text-xs text-[var(--pixel-text-muted)] mb-4">
        {hasDirectoryPicker
          ? 'Elegir carpeta usa tu ordenador (Chrome/Edge). Ruta en el servidor usa la máquina donde corre el backend.'
          : 'Ruta en el servidor (ej: /ruta/local). El backend escanea ese directorio.'}
      </p>
      <p className="text-xs text-[var(--pixel-text-on-dark)] mb-2">
        Para carpetas con muchos archivos o rutas protegidas, usa la <strong>ruta en el servidor</strong>. Si el navegador bloquea la carpeta, elige otra o usa la ruta del servidor.
      </p>
      {!hasDirectoryPicker && (
        <p className="text-xs text-amber-600 dark:text-amber-400 mb-2">
          Para usar una carpeta de tu ordenador, usa Chrome o Edge, o ejecuta el backend en tu máquina e indica la ruta local del servidor.
        </p>
      )}
      <div className="flex gap-2 flex-wrap mb-4">
        {hasDirectoryPicker && (
          <Button onClick={handlePickFolder} disabled={loading} className="px-4 py-2">
            {loading ? 'ESCANEANDO...' : 'ELEGIR CARPETA LOCAL'}
          </Button>
        )}
        <Input
          placeholder="Ruta en el servidor (ej: /ruta/local)"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleScanServer()}
          className="flex-1 min-w-[200px]"
        />
        <Button onClick={handleScanServer} disabled={loading} className="px-4 py-2">
          ESCANEAR SERVIDOR
        </Button>
      </div>
      {loading && (
        <div className="mb-4 max-w-md">
          <ProgressBar
            percent={progressPercent}
            indeterminate={progressIndeterminate}
            label={progressFiles != null ? `Archivos escaneados: ${progressFiles}` : 'Escaneando...'}
          />
        </div>
      )}
      {stats && !selectedExtension && !detailFile && (
        <Card className="results-block p-4 mt-4 animate-view-in">
          <h2 className="pixel-section-title mb-2">Resultados</h2>
          <p className="text-xs text-[var(--pixel-text-on-dark)] mb-2">Archivos: {stats.total_files} — Tamaño total: {(stats.total_size / 1024).toFixed(1)} KB</p>
          {Object.keys(stats.by_extension || {}).length > 0 && (
            <>
              <p className="text-xs text-[var(--pixel-text-muted)] mt-2">Por extensión (clic para ver lista):</p>
              <ul className="text-xs mt-1 space-y-0.5">
                {Object.entries(stats.by_extension)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 25)
                  .map(([ext, count]) => (
                    <li key={ext}>
                      <button
                        type="button"
                        onClick={() => handleSelectExtension(ext)}
                        className="text-[var(--pixel-accent)] hover:underline text-left"
                      >
                        {ext}: {count}
                      </button>
                    </li>
                  ))}
              </ul>
            </>
          )}
        </Card>
      )}
      {selectedExtension && !detailFile && (
        <Card className="results-block p-4 mt-4 animate-view-in">
          <div className="flex items-center gap-2 mb-2">
            <button
              type="button"
              onClick={() => { setSelectedExtension(null); setFilesFromServer(null) }}
              className="text-xs text-[var(--pixel-accent)] hover:underline"
            >
              ← Volver a resultados
            </button>
          </div>
          <h2 className="pixel-section-title mb-2">Archivos {selectedExtension}</h2>
          {loadingFiles ? (
            <p className="text-xs text-[var(--pixel-text-muted)]">Cargando...</p>
          ) : (
            <div className="max-h-[70vh] overflow-y-auto">
              <Table
                columns={[
                  { key: 'name', label: 'Nombre' },
                  { key: 'size', label: 'Tamaño', align: 'right' },
                ]}
                data={currentFileList.map((f) => ({
                  name: f.name,
                  size: f.size ?? f.size_bytes,
                  path: f.path,
                  mime_type: f.mime_type,
                }))}
                emptyMessage="No hay archivos."
                renderCell={(key, value, row) => (key === 'size' ? formatSize(value) : value)}
                onRowClick={(row) => setDetailFile(row)}
              />
            </div>
          )}
        </Card>
      )}
      {detailFile && (
        <Card className="results-block p-4 mt-4 animate-view-in">
          <div className="flex flex-col gap-2 mb-2">
            <button
              type="button"
              onClick={() => setDetailFile(null)}
              className="text-xs text-[var(--pixel-accent)] hover:underline w-fit"
            >
              Volver a la tabla
            </button>
          </div>
          <h2 className="pixel-section-title mb-2">Detalle</h2>
          <dl className="text-xs text-[var(--pixel-text-on-dark)] space-y-1">
            <dt className="text-[var(--pixel-text-muted)]">Nombre</dt>
            <dd className="mb-2 text-[var(--pixel-text-in)]">{detailFile.name}</dd>
            {detailFile.path && (
              <>
                <dt className="text-[var(--pixel-text-muted)]">Ruta</dt>
                <dd className="mb-2 break-all text-[var(--pixel-text-in)]">{detailFile.path}</dd>
              </>
            )}
            <dt className="text-[var(--pixel-text-muted)]">Tamaño</dt>
            <dd className="mb-2">{formatSize(detailFile.size ?? detailFile.size_bytes)}</dd>
            {detailFile.mime_type && (
              <>
                <dt className="text-[var(--pixel-text-muted)]">Tipo</dt>
                <dd>{detailFile.mime_type}</dd>
              </>
            )}
          </dl>
        </Card>
      )}
    </AnimatedView>
  )
}
