/**
 * Import.jsx - Importar por ruta en el servidor o desde carpeta local (File System Access API).
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useMage } from '../context/MageContext'
import { useToast } from '../context/ToastContext'
import { friendlyMessage } from '../utils/toastMessages'
import { importPath, uploadDocuments } from '../services/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { AnimatedView } from '../components/AnimatedView'

const hasDirectoryPicker = typeof window !== 'undefined' && typeof window.showDirectoryPicker === 'function'

const SUPPORTED_EXTENSIONS = new Set([
  '.pdf', '.txt', '.md', '.rst', '.log', '.csv', '.docx', '.xlsx',
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.tif',
  '.heic', '.heif',
  '.mov', '.mp4', '.avi', '.mkv', '.webm', '.m4v', '.wmv', '.flv',
  '.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma',
  '.c', '.h', '.java', '.py', '.js', '.ts', '.go', '.rs', '.sh', '.bat',
  '.exe', '.dll', '.so', '.dylib',
])
const MAX_FILES_IMPORT = 500
const UPLOAD_BATCH_SIZE = 50

async function* walkDirectory(handle) {
  for await (const entry of handle.values()) {
    if (entry.kind === 'file') {
      yield await entry.getFile()
    } else if (entry.kind === 'directory') {
      yield* walkDirectory(entry)
    }
  }
}

function hasSupportedExtension(name) {
  const i = name.lastIndexOf('.')
  if (i === -1) return false
  return SUPPORTED_EXTENSIONS.has('.' + name.slice(i + 1).toLowerCase())
}

export function Import() {
  const { token } = useAuth()
  const { sayForScene } = useMage()
  const { addToast } = useToast()
  const [path, setPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(null)

  useEffect(() => {
    sayForScene('import')
  }, [sayForScene])

  const handleImportServer = async () => {
    if (!path.trim()) {
      addToast('Indica una ruta.', 'error')
      return
    }
    setLoading(true)
    setMessage('')
    setProgress(null)
    try {
      const data = await importPath(token, path.trim())
      setMessage(`Importados: ${data.imported ?? 0}.`)
    } catch (err) {
      addToast(friendlyMessage(err.message) || 'Error al importar', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handlePickFolder = async () => {
    if (!hasDirectoryPicker) return
    setLoading(true)
    setMessage('')
    setProgress({ current: 0, total: 0 })
    try {
      const dir = await window.showDirectoryPicker()
      const files = []
      for await (const file of walkDirectory(dir)) {
        if (hasSupportedExtension(file.name)) {
          files.push(file)
          if (files.length >= MAX_FILES_IMPORT) break
        }
      }
      setProgress({ current: 0, total: files.length })
      if (files.length === 0) {
        addToast('No se encontraron archivos con extensiones soportadas.', 'warning')
        setLoading(false)
        setProgress(null)
        return
      }
      let imported = 0
      for (let i = 0; i < files.length; i += UPLOAD_BATCH_SIZE) {
        const batch = files.slice(i, i + UPLOAD_BATCH_SIZE)
        const data = await uploadDocuments(token, batch)
        imported += data.imported ?? 0
        setProgress({ current: Math.min(i + UPLOAD_BATCH_SIZE, files.length), total: files.length })
      }
      setMessage(`Importados: ${imported}.`)
    } catch (err) {
      if (err.name === 'AbortError') {
        setLoading(false)
        setProgress(null)
        return
      }
      addToast(friendlyMessage(err.message) || 'Error al importar', 'error')
    } finally {
      setLoading(false)
      setProgress(null)
    }
  }

  return (
    <AnimatedView className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-6 border-b-2 border-[var(--pixel-border)] pb-4">
        <Link to="/" className="link-back-menu">
          ← Volver al menú
        </Link>
      </header>
      <h1 className="text-lg text-[var(--pixel-accent)] mb-4">Import documents</h1>
      <p className="text-xs text-[var(--pixel-muted)] mb-4">
        {hasDirectoryPicker
          ? 'Elegir carpeta usa tu ordenador (Chrome/Edge). Ruta en el servidor usa la máquina donde corre el backend.'
          : 'Ruta en el servidor (archivo o carpeta). Se añadira al indice.'}
      </p>
      {!hasDirectoryPicker && (
        <p className="text-xs text-amber-600 dark:text-amber-400 mb-2">
          Para usar una carpeta de tu ordenador, usa Chrome o Edge, o ejecuta el backend en tu máquina e indica la ruta local del servidor.
        </p>
      )}
      <div className="flex gap-2 flex-wrap mb-4">
        {hasDirectoryPicker && (
          <Button onClick={handlePickFolder} disabled={loading} className="px-4 py-2">
            {loading && progress ? `IMPORTANDO ${progress.current} DE ${progress.total}...` : loading ? 'PREPARANDO...' : 'ELEGIR CARPETA PARA IMPORTAR'}
          </Button>
        )}
        <Input
          placeholder="Ruta en el servidor (ej: /ruta/local)"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleImportServer()}
          className="flex-1 min-w-[200px]"
        />
        <Button onClick={handleImportServer} disabled={loading} className="px-4 py-2">
          {loading && !progress ? 'IMPORTANDO...' : 'IMPORTAR SERVIDOR'}
        </Button>
      </div>
      {message && <p className="text-[var(--pixel-accent)] text-xs">{message}</p>}
    </AnimatedView>
  )
}
